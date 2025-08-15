import socket
from shared.config import HOST_SERVER, PORT_CHAT, BUFFER_SIZE, ENCODING

class Server:
    def __init__(self, host=HOST_SERVER, port=PORT_CHAT):
        self.host = host
        self.port = port
        self.server_socket = None
        self.client_socket = None
        self.client_address = None

    def start(self):
        """Khởi động server và lắng nghe kết nối"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(1)
            print(f"[SERVER] Đang lắng nghe trên {self.host}:{self.port}...")
            
            self.client_socket, self.client_address = self.server_socket.accept()
            print(f"[SERVER] Đã kết nối với client từ {self.client_address}")
        except Exception as e:
            print(f"[ERROR] Không thể khởi động server: {e}")

    def receive_message(self):
        """Nhận tin nhắn từ client"""
        try:
            data = self.client_socket.recv(BUFFER_SIZE).decode(ENCODING)
            return data
        except Exception as e:
            print(f"[ERROR] Nhận tin nhắn thất bại: {e}")
            return None

    def send_message(self, msg):
        """Gửi tin nhắn tới client"""
        try:
            self.client_socket.sendall(msg.encode(ENCODING))
        except Exception as e:
            print(f"[ERROR] Gửi tin nhắn thất bại: {e}")

    def close(self):
        """Đóng kết nối"""
        if self.client_socket:
            self.client_socket.close()
        if self.server_socket:
            self.server_socket.close()
        print("[SERVER] Đã đóng kết nối")


if __name__ == "__main__":
    server = Server()
    server.start()

    try:
        while True:
            # Nhận tin nhắn từ client
            message = server.receive_message()
            if not message or message.lower() == "/quit":
                break
            
            print(f"Client: {message}")
            
            # Gửi phản hồi
            reply = input("Server: ")
            server.send_message(reply)
            
    except KeyboardInterrupt:
        pass
    finally:
        server.close()