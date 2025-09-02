# chat_handler.py
import socket
import threading
import json
from shared import config

class ChatHandler:
    def __init__(self, host=config.HOST_CLIENT_CONNECT, port=config.PORT_CHAT, username="User", history_manager=None):
        self.host = host
        self.port = port
        self.username = username
        self.client_socket = None
        self.running = False
        self.room_id = None
        self.history_manager = history_manager

    def connect(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
            self.running = True
            return True, f"Đã kết nối tới server {self.host}:{self.port}"
        except Exception as e:
            return False, f"Không thể kết nối server chat: {e}"

    def join_room(self, room_id="general", password=""):
        """Yêu cầu join room"""
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

    def leave_room(self):
        """Rời phòng"""
        if not self.room_id:
            return False, "Chưa tham gia phòng nào"
        try:
            data = {"type": "LEAVE_ROOM", "username": self.username, "room_id": self.room_id}
            self.client_socket.sendall(json.dumps(data).encode(config.ENCODING))
            self.room_id = None
            return True, "Đã gửi yêu cầu rời phòng"
        except Exception as e:
            return False, f"Lỗi khi rời phòng: {e}"

    def send_message(self, message):
        """Gửi chat message"""
        if not self.room_id:
            return False, "Chưa tham gia phòng"
        try:
            data = {
                "type": "CHAT_MESSAGE",
                "username": self.username,
                "room_id": self.room_id,
                "message": message
            }
            self.client_socket.sendall(json.dumps(data).encode(config.ENCODING))
            return True, "Đã gửi tin nhắn"
        except Exception as e:
            return False, f"Lỗi gửi tin nhắn: {e}"

    def receive_messages(self, callback):
        """Lắng nghe tin nhắn từ server"""
        def listen():
            while self.running:
                try:
                    data = self.client_socket.recv(config.BUFFER_SIZE).decode(config.ENCODING)
                    if not data:
                        callback({"type": "ERROR", "message": "Connection closed by server"})
                        break
                    try:
                        msg_data = json.loads(data)
                    except json.JSONDecodeError:
                        msg_data = {"type": "TEXT", "message": data}

                    # lưu lịch sử nếu là chat
                    if msg_data.get("type") == "CHAT_MESSAGE" and self.history_manager:
                        self.history_manager.add_chat_entry(
                            msg_data.get("username", "Unknown"),
                            msg_data.get("message", "")
                        )

                    callback(msg_data)
                except ConnectionResetError:
                    callback({"type": "ERROR", "message": "Connection reset by peer"})
                    break
                except Exception as e:
                    callback({"type": "ERROR", "message": f"Receive error: {str(e)}"})
                    break
        threading.Thread(target=listen, daemon=True).start()

    def close(self):
        self.running = False
        if self.client_socket:
            self.client_socket.close()
            self.client_socket = None
