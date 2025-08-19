import socket
import threading
import json
import time
from collections import defaultdict
from shared.config import HOST_SERVER_BIND, PORT_CHAT, BUFFER_SIZE, ENCODING

class ChatServer:
    def __init__(self, callback=None):
        self.callback = callback
        self.running = False
        self.server_socket = None

        # Quản lý các kết nối chat
        self.chat_clients = []  # Danh sách tất cả client chat
        self.chat_rooms = defaultdict(list)  # {room_id: [client_sockets]} cho chat
        self.client_info = {}  # {client_socket: (username, room_id)}

    def start(self):
        """Khởi động chat server"""
        if self.running:
            return
            
        self.running = True
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((HOST_SERVER_BIND, PORT_CHAT))
        self.server_socket.listen(10)  # Tăng số lượng kết nối tối đa

        if self.callback:
            self.callback("SERVER_STARTED", f"Chat server đang chạy trên {HOST_SERVER_BIND}:{PORT_CHAT}")
        else:
            print(f"[CHAT SERVER] Đang chạy trên {HOST_SERVER_BIND}:{PORT_CHAT}")

        # Thread chấp nhận kết nối mới
        threading.Thread(target=self._accept_connections, daemon=True).start()

    def stop(self):
        """Dừng chat server"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        self._cleanup()

    def _accept_connections(self):
        """Chấp nhận kết nối mới từ client"""
        while self.running:
            try:
                client_socket, addr = self.server_socket.accept()
                
                if self.callback:
                    self.callback("NEW_CHAT_CONNECTION", f"Kết nối chat mới từ {addr}")
                else:
                    print(f"[CHAT SERVER] Kết nối mới từ {addr}")

                # Thêm client vào danh sách
                self.chat_clients.append(client_socket)

                # Bắt đầu thread xử lý client
                threading.Thread(
                    target=self._handle_chat_client,
                    args=(client_socket,),
                    daemon=True
                ).start()
                
            except Exception as e:
                if self.callback:
                    self.callback("ACCEPT_ERROR", f"Lỗi chấp nhận kết nối: {e}")
                else:
                    print(f"[CHAT SERVER] Lỗi chấp nhận kết nối: {e}")
                time.sleep(1)

    def _handle_chat_client(self, client_socket):
        """Xử lý kết nối chat từ một client"""
        username = "Unknown"
        room_id = None
        
        try:
            while self.running:
                # Nhận dữ liệu từ client
                data = client_socket.recv(BUFFER_SIZE)
                if not data:
                    break
                    
                try:
                    # Parse JSON message
                    message_data = json.loads(data.decode(ENCODING))
                    message_type = message_data.get("type", "")
                    
                    if message_type == "JOIN_ROOM":
                        # Client muốn tham gia phòng chat
                        username = message_data.get("username", "Unknown")
                        room_id = message_data.get("room_id", "general")
                        password = message_data.get("password", "")
                        
                        # Thêm client vào phòng chat
                        self._join_chat_room(client_socket, room_id, username, password)
                        
                    elif message_type == "CHAT_MESSAGE":
                        # Client gửi tin nhắn chat
                        username = message_data.get("username", "Unknown")
                        message = message_data.get("message", "")
                        room_id = message_data.get("room_id", "general")
                        
                        # Broadcast tin nhắn tới phòng
                        self._broadcast_chat_message(room_id, username, message, client_socket)
                        
                    elif message_type == "LEAVE_ROOM":
                        # Client rời phòng
                        self._leave_chat_room(client_socket, room_id, username)
                        break
                        
                except json.JSONDecodeError:
                    # Xử lý tin nhắn plain text (cho tương thích ngược)
                    message = data.decode(ENCODING)
                    if message.startswith("/join "):
                        parts = message.split(" ")
                        if len(parts) >= 3:
                            username = parts[1]
                            room_id = parts[2]
                            self._join_chat_room(client_socket, room_id, username, "")
                    else:
                        self._broadcast_chat_message(room_id or "general", username, message, client_socket)
                        
        except ConnectionResetError:
            if self.callback:
                self.callback("CHAT_DISCONNECTED", f"{username} đã ngắt kết nối chat")
            else:
                print(f"[CHAT SERVER] {username} đã ngắt kết nối chat")
        except Exception as e:
            if self.callback:
                self.callback("CHAT_ERROR", f"Lỗi xử lý chat {username}: {e}")
            else:
                print(f"[CHAT SERVER] Lỗi xử lý chat {username}: {e}")
        finally:
            self._remove_chat_client(client_socket, room_id, username)

    def _join_chat_room(self, client_socket, room_id, username, password):
        """Thêm client vào phòng chat"""
        # Kiểm tra mật khẩu nếu cần (có thể implement sau)
        if room_id not in self.chat_rooms:
            self.chat_rooms[room_id] = []
            
        self.chat_rooms[room_id].append(client_socket)
        self.client_info[client_socket] = (username, room_id)

        # Thông báo client đã tham gia phòng
        join_message = {
            "type": "SYSTEM",
            "message": f"{username} đã tham gia phòng chat",
            "username": "System",
            "room_id": room_id
        }
        self._send_to_client(client_socket, join_message)

        # Thông báo cho các client khác trong phòng
        notification = {
            "type": "USER_JOINED",
            "username": username,
            "room_id": room_id,
            "message": f"{username} đã tham gia phòng chat"
        }
        self._broadcast_to_room(room_id, notification, client_socket)

        if self.callback:
            self.callback("CHAT_JOIN", f"{username} đã tham gia phòng {room_id}")
        else:
            print(f"[CHAT SERVER] {username} đã tham gia phòng {room_id}")

    def _broadcast_chat_message(self, room_id, username, message, sender_socket):
        """Broadcast tin nhắn chat tới phòng"""
        if room_id not in self.chat_rooms:
            return
            
        chat_data = {
            "type": "CHAT_MESSAGE",
            "username": username,
            "message": message,
            "room_id": room_id,
            "timestamp": time.strftime("%H:%M:%S")
        }
        
        self._broadcast_to_room(room_id, chat_data, sender_socket)
        
        if self.callback:
            self.callback("CHAT_MESSAGE", f"{username} trong {room_id}: {message}")
        else:
            print(f"[CHAT SERVER] {username} trong {room_id}: {message}")

    def _leave_chat_room(self, client_socket, room_id, username):
        """Xử lý client rời phòng chat"""
        self._remove_chat_client(client_socket, room_id, username)
        
        # Thông báo cho các client khác
        if room_id in self.chat_rooms:
            leave_message = {
                "type": "USER_LEFT",
                "username": username,
                "room_id": room_id,
                "message": f"{username} đã rời phòng chat"
            }
            self._broadcast_to_room(room_id, leave_message)

    def _broadcast_to_room(self, room_id, data, exclude_socket=None):
        """Broadcast dữ liệu JSON tới phòng"""
        if room_id not in self.chat_rooms:
            return
            
        json_data = json.dumps(data, ensure_ascii=False).encode(ENCODING)
        disconnected_clients = []
        
        for client in self.chat_rooms[room_id]:
            if client != exclude_socket:
                try:
                    client.sendall(json_data)
                except:
                    disconnected_clients.append(client)
                    
        # Dọn dẹp client disconnect
        for client in disconnected_clients:
            self._remove_chat_client(client, room_id, "Unknown")

    def _send_to_client(self, client_socket, data):
        """Gửi dữ liệu JSON tới client"""
        try:
            json_data = json.dumps(data, ensure_ascii=False)
            client_socket.sendall(json_data.encode(ENCODING))
        except:
            pass

    def _remove_chat_client(self, client_socket, room_id, username):
        """Xóa client khỏi hệ thống chat"""
        # Xóa khỏi danh sách chung
        if client_socket in self.chat_clients:
            self.chat_clients.remove(client_socket)

        # Xóa khỏi phòng chat
        if room_id and room_id in self.chat_rooms and client_socket in self.chat_rooms[room_id]:
            self.chat_rooms[room_id].remove(client_socket)

            # Xóa phòng nếu trống
            if not self.chat_rooms[room_id]:
                del self.chat_rooms[room_id]

        # Xóa thông tin client
        if client_socket in self.client_info:
            del self.client_info[client_socket]

        # Đóng socket
        try:
            client_socket.close()
        except:
            pass

    def _cleanup(self):
        """Dọn dẹp tài nguyên"""
        for client in self.chat_clients[:]:
            try:
                client.close()
            except:
                pass
                
        self.chat_clients.clear()
        self.chat_rooms.clear()
        self.client_info.clear()

    def _broadcast_system_message(self, room_id, message):
        """Broadcast system message"""
        system_msg = {
            "type": "SYSTEM",
            "message": message,
            "room_id": room_id,
            "timestamp": time.strftime("%H:%M:%S")
        }
        self._broadcast_to_room(room_id, system_msg)

    def _broadcast_user_joined(self, room_id, username):
        """Broadcast khi có user mới tham gia"""
        self._broadcast_system_message(room_id, f"👋 {username} đã tham gia phòng chat")

    def _broadcast_user_left(self, room_id, username):
        """Broadcast khi user rời phòng"""
        self._broadcast_system_message(room_id, f"🚪 {username} đã rời phòng chat")

if __name__ == "__main__":
    def chat_status_handler(event, message):
        print(f"[CHAT {event}] {message}")

    server = ChatServer(callback=chat_status_handler)
    try:
        server.start()
        print("Chat server đang chạy... Nhấn Ctrl+C để dừng")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server.stop()
        print("Chat server đã dừng")