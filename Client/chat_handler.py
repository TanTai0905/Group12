import socket
import threading
import json
from shared import config

class ChatHandler:
    """
    Lớp quản lý kết nối chat: gửi/nhận tin nhắn.
    Thiết kế để tích hợp trực tiếp vào GUI.
    """
    def __init__(self, host=config.HOST, port=config.PORT, username="User"):
        self.host = host
        self.port = port
        self.username = username
        self.client_socket = None
        self.running = False

    def connect(self):
        """Kết nối tới server chat"""
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
            self.running = True
            return True, f"Đã kết nối tới server {self.host}:{self.port}"
        except Exception as e:
            return False, f"Không thể kết nối server chat: {e}"

    def send_message(self, message):
        """Gửi tin nhắn đến server"""
        if not self.client_socket or not self.running:
            return False, "Chưa kết nối server"
        try:
            data = {
                "type": "CHAT",
                "username": self.username,
                "message": message
            }
            self.client_socket.sendall(json.dumps(data).encode(config.ENCODING))
            return True, "Đã gửi tin nhắn"
        except Exception as e:
            return False, f"Gửi tin nhắn thất bại: {e}"

    def receive_messages(self, callback):
        """
        Nhận tin nhắn từ server và gọi callback(msg_data)
        msg_data = {"type": "CHAT", "username": ..., "message": ...}
        """
        def listen():
            while self.running:
                try:
                    data = self.client_socket.recv(config.BUFFER_SIZE).decode(config.ENCODING)
                    if not data:
                        break
                    try:
                        msg_data = json.loads(data)
                    except json.JSONDecodeError:
                        msg_data = {"type": "TEXT", "message": data}
                    callback(msg_data)
                except Exception as e:
                    callback({"type": "ERROR", "message": str(e)})
                    break
        threading.Thread(target=listen, daemon=True).start()

    def close(self):
        """Đóng kết nối"""
        self.running = False
        if self.client_socket:
            self.client_socket.close()
            self.client_socket = None
