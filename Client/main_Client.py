import socket
from shared.config import HOST_CLIENT_CONNECT, PORT_CHAT, BUFFER_SIZE, ENCODING

class Client:
    def __init__(self, host=HOST_CLIENT_CONNECT, port=PORT_CHAT):
        self.host = host
        self.port = port
        self.client_socket = None

    def connect(self):
        """Kết nối tới server"""
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
            print(f"[CLIENT] Kết nối tới server {self.host}:{self.port} thành công")
        except Exception as e:
            print(f"[ERROR] Không thể kết nối server: {e}")

    def send_message(self, msg):
        """Gửi tin nhắn tới server"""
        try:
            self.client_socket.sendall(msg.encode(ENCODING))
        except Exception as e:
            print(f"[ERROR] Gửi tin nhắn thất bại: {e}")

    def receive_message(self):
        """Nhận tin nhắn từ server"""
        try:
            data = self.client_socket.recv(BUFFER_SIZE).decode(ENCODING)
            return data
        except Exception as e:
            print(f"[ERROR] Nhận tin nhắn thất bại: {e}")
            return None

    def close(self):
        """Đóng kết nối"""
        if self.client_socket:
            self.client_socket.close()
            print("[CLIENT] Đã đóng kết nối")

if __name__ == "__main__":
    client = Client()
    client.connect()

    try:
        while True:
            msg = input("Bạn: ")
            if msg.lower() == "/quit":
                break
            client.send_message(msg)
            reply = client.receive_message()
            if reply:
                print("Server:", reply)
    except KeyboardInterrupt:
        pass
    finally:
        client.close()
