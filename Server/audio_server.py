import socket
import threading
import pyaudio
import secrets
import time
import json
from collections import defaultdict
from shared.config import HOST_SERVER_BIND, PORT_AUDIO, BUFFER_SIZE, ENCODING, AUDIO_CHUNK, AUDIO_RATE, AUDIO_CHANNELS

class AudioServer:
    def __init__(self, callback=None):
        self.callback = callback
        self.running = False
        self.server_socket = None
        self.audio = pyaudio.PyAudio()

        # Quản lý phòng chat
        self.audio_rooms = defaultdict(list)  # {room_id: [client_sockets]}
        self.room_passwords = {}  # {room_id: password}
        self.client_info = {}  # {client_socket: (room_id, username)}

        # Audio config
        self.chunk = AUDIO_CHUNK
        self.rate = AUDIO_RATE
        self.channels = AUDIO_CHANNELS
        self.format = pyaudio.paInt16

    def start(self):
        """Khởi động server audio"""
        if self.running:
            return
            
        self.running = True
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((HOST_SERVER_BIND, PORT_AUDIO))
        self.server_socket.listen(5)
        
        self._notify("SERVER_STARTED", f"Audio server đang chạy trên {HOST_SERVER_BIND}:{PORT_AUDIO}")

        # Thread chấp nhận kết nối mới
        threading.Thread(target=self._accept_connections, daemon=True).start()

    def stop(self):
        """Dừng server"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        self._cleanup()

    def _generate_room_id(self):
        """Tạo mã phòng ngẫu nhiên 6 ký tự"""
        return secrets.token_hex(3).upper()

    def _accept_connections(self):
        """Chấp nhận kết nối mới từ client"""
        while self.running:
            try:
                client_socket, addr = self.server_socket.accept()
                self._notify("NEW_CONNECTION", f"Kết nối mới từ {addr}")

                # Nhận thông tin đăng nhập từ client
                init_data = client_socket.recv(BUFFER_SIZE).decode(ENCODING).split("|")
                
                if init_data[0] == "CREATE":
                    # Tạo phòng mới
                    room_id = self._generate_room_id()
                    username = init_data[1]
                    password = init_data[2] if len(init_data) > 2 else None
                    
                    self.audio_rooms[room_id].append(client_socket)
                    self.client_info[client_socket] = (room_id, username)
                    
                    if password:
                        self.room_passwords[room_id] = password
                    
                    client_socket.sendall(f"ROOM_CREATED|{room_id}".encode(ENCODING))
                    self._notify("ROOM_CREATED", f"{username} đã tạo phòng {room_id}")
                    
                elif init_data[0] == "JOIN":
                    # Tham gia phòng có sẵn
                    room_id = init_data[1]
                    username = init_data[2]
                    password = init_data[3] if len(init_data) > 3 else None
                    
                    if room_id not in self.audio_rooms:
                        client_socket.sendall("ERROR|Phòng không tồn tại".encode(ENCODING))
                        client_socket.close()
                        continue
                        
                    if room_id in self.room_passwords and self.room_passwords[room_id] != password:
                        client_socket.sendall("ERROR|Mật khẩu sai".encode(ENCODING))
                        client_socket.close()
                        continue
                        
                    self.audio_rooms[room_id].append(client_socket)
                    self.client_info[client_socket] = (room_id, username)
                    client_socket.sendall(f"JOIN_SUCCESS|{room_id}".encode(ENCODING))
                    self._notify("JOIN_ROOM", f"{username} đã tham gia phòng {room_id}")
                    
                    # Broadcast danh sách user mới
                    self._broadcast_user_list(room_id)

                # Bắt đầu thread xử lý client
                threading.Thread(
                    target=self._handle_client,
                    args=(client_socket,),
                    daemon=True
                ).start()
                
            except Exception as e:
                self._notify("ACCEPT_ERROR", str(e))
                time.sleep(1)

    def _handle_client(self, client_socket):
        """Xử lý luồng âm thanh từ một client"""
        if client_socket not in self.client_info:
            return
            
        room_id, username = self.client_info[client_socket]
        
        try:
            while self.running:
                # Nhận dữ liệu âm thanh từ client
                audio_data = client_socket.recv(self.chunk)
                if not audio_data:
                    break
                    
                # Gửi dữ liệu tới tất cả client khác trong phòng
                self._broadcast_audio(audio_data, room_id, client_socket)
                
        except ConnectionResetError:
            self._notify("CLIENT_DISCONNECTED", f"{username} đã ngắt kết nối")
        except Exception as e:
            self._notify("CLIENT_ERROR", f"Lỗi với {username}: {str(e)}")
        finally:
            self._remove_client(client_socket, room_id, username)

    def _broadcast_to_room(self, room_id, data, exclude_socket=None):
        """
        Broadcast dữ liệu tới tất cả client trong phòng
        data: có thể là audio data hoặc system message
        """
        if room_id not in self.audio_rooms:
            return
            
        disconnected_clients = []
        
        for client in self.audio_rooms[room_id]:
            if client != exclude_socket:
                try:
                    client.sendall(data)
                except:
                    # Client đã ngắt kết nối
                    disconnected_clients.append(client)
                    
        # Dọn dẹp client đã disconnect
        for client in disconnected_clients:
            if client in self.client_info:
                room, username = self.client_info[client]
                self._remove_client(client, room, username)

    def _broadcast_audio(self, audio_data, room_id, sender_socket):
        """Broadcast audio data tới phòng"""
        self._broadcast_to_room(room_id, audio_data, sender_socket)

    def _broadcast_system_message(self, room_id, message):
        """Broadcast system message dạng JSON"""
        system_msg = json.dumps({
            "type": "SYSTEM",
            "message": message,
            "timestamp": time.strftime("%H:%M:%S")
        }, ensure_ascii=False).encode(ENCODING)
        
        # Thêm header để client phân biệt
        header = b"SYS_MSG|"
        self._broadcast_to_room(room_id, header + system_msg)

    def _broadcast_user_list(self, room_id):
        """Broadcast danh sách user trong phòng"""
        if room_id not in self.audio_rooms:
            return
            
        users = []
        for client in self.audio_rooms[room_id]:
            if client in self.client_info:
                users.append(self.client_info[client][1])
                
        user_list_msg = json.dumps({
            "type": "USER_LIST",
            "users": users,
            "room_id": room_id
        }, ensure_ascii=False).encode(ENCODING)
        
        header = b"USER_LIST|"
        self._broadcast_to_room(room_id, header + user_list_msg)

    def _remove_client(self, client_socket, room_id, username):
        """Xóa client khỏi phòng khi ngắt kết nối"""
        if room_id in self.audio_rooms and client_socket in self.audio_rooms[room_id]:
            self.audio_rooms[room_id].remove(client_socket)
            self._notify("LEFT_ROOM", f"{username} đã rời khỏi phòng {room_id}")
            
            # Broadcast danh sách user mới
            self._broadcast_user_list(room_id)

        # Xóa thông tin client
        if client_socket in self.client_info:
            del self.client_info[client_socket]

        # Đóng socket
        try:
            client_socket.close()
        except:
            pass

        # Nếu phòng trống thì xóa phòng
        if room_id in self.audio_rooms and not self.audio_rooms[room_id]:
            del self.audio_rooms[room_id]
            if room_id in self.room_passwords:
                del self.room_passwords[room_id]
            self._notify("ROOM_CLOSED", f"Phòng {room_id} đã đóng")

    def _cleanup(self):
        """Dọn dẹp tài nguyên"""
        for room_id in list(self.audio_rooms.keys()):
            for client in self.audio_rooms[room_id]:
                try:
                    client.close()
                except:
                    pass
                    
        self.audio_rooms.clear()
        self.room_passwords.clear()
        self.client_info.clear()
        self.audio.terminate()

    def _notify(self, event, message=""):
        """Gửi thông báo tới callback (nếu có)"""
        if self.callback:
            self.callback(event, message)

if __name__ == "__main__":
    def status_handler(event, message):
        print(f"[{event}] {message}")

    server = AudioServer(callback=status_handler)
    try:
        server.start()
        print("Audio server đang chạy... Nhấn Ctrl+C để dừng")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server.stop()
        print("Audio server đã dừng")