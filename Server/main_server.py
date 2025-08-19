import socket
import threading
import time
from shared.config import HOST_SERVER_BIND, PORT_CHAT, PORT_AUDIO, BUFFER_SIZE, ENCODING
from Server.audio_server import AudioServer
from Server.chat_server import ChatServer
from Server.client_handler import ClientHandler

class MainServer:
    def __init__(self):
        self.running = False
        self.chat_server = None
        self.audio_server = None
        self.text_server_socket = None
        self.connected_clients = []

    def start(self):
        """Khởi động tất cả các server"""
        if self.running:
            return
            
        self.running = True
        
        print("=" * 60)
        print("🌟 MAIN SERVER - HỆ THỐNG CHAT VOICE & TEXT")
        print("=" * 60)

        # Khởi động Chat Server
        self.chat_server = ChatServer(callback=self._handle_chat_event)
        self.chat_server.start()
        print(f"✅ Chat Server : {HOST_SERVER_BIND}:{PORT_CHAT}")

        # Khởi động Audio Server
        self.audio_server = AudioServer(callback=self._handle_audio_event)
        self.audio_server.start()
        print(f"✅ Audio Server : {HOST_SERVER_BIND}:{PORT_AUDIO}")

        # Khởi động Text Server (tương thích ngược)
        self._start_text_server()
        print(f"✅ Text Server : {HOST_SERVER_BIND}:{PORT_CHAT} (Legacy)")

        print("=" * 60)
        print("🚀 Tất cả server đã khởi động thành công!")
        print("📊 Đang chờ kết nối từ clients...")
        print("⏹️ Nhấn Ctrl+C để dừng server")
        print("=" * 60)

        # Thread monitor hệ thống
        threading.Thread(target=self._system_monitor, daemon=True).start()

    def stop(self):
        """Dừng tất cả các server"""
        self.running = False
        print("\n🛑 Đang dừng server...")
        
        if self.chat_server:
            self.chat_server.stop()
            print("✅ Chat server đã dừng")
            
        if self.audio_server:
            self.audio_server.stop()
            print("✅ Audio server đã dừng")
            
        if self.text_server_socket:
            self.text_server_socket.close()
            print("✅ Text server đã dừng")

        # Đóng tất cả client connections
        for client in self.connected_clients:
            try:
                client.close()
            except:
                pass
                
        self.connected_clients.clear()
        print("🎯 Tất cả server đã dừng hoàn toàn")

    def _start_text_server(self):
        """Khởi động text server cho client cũ (tương thích ngược)"""
        def handle_text_client(client_socket, client_address):
            """Xử lý client kết nối text (legacy)"""
            print(f"📨 Legacy client kết nối: {client_address}")
            client_handler = ClientHandler(client_socket, client_address)
            client_handler.start()
            self.connected_clients.append(client_socket)

        self.text_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.text_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.text_server_socket.bind((HOST_SERVER_BIND, PORT_CHAT))
            self.text_server_socket.listen(10)
            
            def accept_text_clients():
                while self.running:
                    try:
                        client_socket, client_address = self.text_server_socket.accept()
                        threading.Thread(
                            target=handle_text_client,
                            args=(client_socket, client_address),
                            daemon=True
                        ).start()
                    except:
                        break
                        
            threading.Thread(target=accept_text_clients, daemon=True).start()
            
        except Exception as e:
            print(f"❌ Lỗi khởi động text server: {e}")

    def _handle_audio_event(self, event, message):
        """Xử lý sự kiện từ audio server"""
        if event in ["ROOM_CREATED", "JOIN_ROOM", "LEFT_ROOM"]:
            print(f"🎤 [AUDIO] {message}")

    def _handle_chat_event(self, event, message):
        """Xử lý sự kiện từ chat server"""
        if event in ["CHAT_MESSAGE", "USER_JOINED", "USER_LEFT"]:
            print(f"💬 [CHAT] {message}")

    def _system_monitor(self):
        """Theo dõi và hiển thị trạng thái hệ thống"""
        while self.running:
            try:
                time.sleep(10)
                self._display_system_status()
            except:
                break

    def _display_system_status(self):
        """Hiển thị trạng thái hệ thống"""
        audio_stats = self._get_audio_stats()
        chat_stats = self._get_chat_stats()
        
        print("\n" + "=" * 60)
        print("📊 BÁO CÁO HỆ THỐNG - " + time.strftime("%H:%M:%S"))
        print("=" * 60)
        print(f"🎤 Audio Rooms: {audio_stats['room_count']}")
        print(f"👥 Audio Users: {audio_stats['user_count']}")
        print(f"💬 Chat Rooms: {chat_stats['room_count']}")
        print(f"👥 Chat Users: {chat_stats['user_count']}")
        print(f"🔗 Total Connections: {len(self.connected_clients)}")
        print("=" * 60)

    def _get_audio_stats(self):
        """Lấy thống kê audio server"""
        try:
            if hasattr(self.audio_server, 'audio_rooms'):
                room_count = len(self.audio_server.audio_rooms)
                user_count = sum(len(clients) for clients in self.audio_server.audio_rooms.values())
                return {"room_count": room_count, "user_count": user_count}
        except:
            pass
        return {"room_count": 0, "user_count": 0}

    def _get_chat_stats(self):
        """Lấy thống kê chat server"""
        try:
            if hasattr(self.chat_server, 'chat_rooms'):
                room_count = len(self.chat_server.chat_rooms)
                user_count = sum(len(clients) for clients in self.chat_server.chat_rooms.values())
                return {"room_count": room_count, "user_count": user_count}
        except:
            pass
        return {"room_count": 0, "user_count": 0}

def main():
    """Hàm chính"""
    server = MainServer()
    try:
        server.start()
        # Giữ chương trình chạy
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server.stop()
    except Exception as e:
        print(f"❌ Lỗi nghiêm trọng: {e}")
        server.stop()

if __name__ == "__main__":
    main()