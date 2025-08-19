import socket
import threading
import json
from shared import config

class ChatHandler:
    def __init__(self, host=config.HOST_CLIENT_CONNECT, port=config.PORT_CHAT, username="User"):
        self.host = host
        self.port = port
        self.username = username
        self.client_socket = None
        self.running = False
        self.room_id = "general"

    def connect(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
            self.running = True
            return True, f"Đã kết nối tới server {self.host}:{self.port}"
        except Exception as e:
            return False, f"Không thể kết nối server chat: {e}"

    def join_room(self, room_id="general", password=""):
        """Gửi yêu cầu join room tới server"""
        self.room_id = room_id
        try:
            data = {
                "type": "JOIN_ROOM",
                "username": self.username,
                "room_id": room_id,
                "password": password
            }
            self.client_socket.sendall(json.dumps(data).encode(config.ENCODING))
            return True, f"Đã gửi yêu cầu tham gia phòng {room_id}"
        except Exception as e:
            return False, f"Lỗi khi join room: {e}"

    def send_message(self, message):
        """Gửi tin nhắn tới server"""
        if not self.client_socket or not self.running:
            return False, "Chưa kết nối server"
        try:
            data = {
                "type": "CHAT_MESSAGE",
                "username": self.username,
                "message": message,
                "room_id": self.room_id
            }
            self.client_socket.sendall(json.dumps(data).encode(config.ENCODING))
            return True, "Đã gửi tin nhắn"
        except Exception as e:
            return False, f"Gửi tin nhắn thất bại: {e}"

    def leave_room(self):
        """Rời khỏi phòng chat"""
        try:
            data = {
                "type": "LEAVE_ROOM",
                "username": self.username,
                "room_id": self.room_id
            }
            self.client_socket.sendall(json.dumps(data).encode(config.ENCODING))
            return True, f"Đã rời phòng {self.room_id}"
        except Exception as e:
            return False, f"Lỗi khi rời phòng: {e}"

    def receive_messages(self, callback):
        """Lắng nghe tin nhắn từ server"""
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
