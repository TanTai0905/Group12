# main_client.py
import socket

class Client:
    def __init__(self, host="127.0.0.1", port=5000):
        self.host = host
        self.port = port
        self.client_socket = None

    def connect(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
            print(f"[CLIENT] Kết nối tới server {self.host}:{self.port} thành công")
        except Exception as e:
            print(f"[ERROR] Không thể kết nối server: {e}")

    def send_message(self, msg):
        try:
            self.client_socket.sendall(msg.encode())
        except Exception as e:
            print(f"[ERROR] Gửi tin nhắn thất bại: {e}")

    def receive_message(self):
        try:
            data = self.client_socket.recv(1024).decode()
            return data
        except Exception as e:
            print(f"[ERROR] Nhận tin nhắn thất bại: {e}")
            return None

    def close(self):
        if self.client_socket:
            self.client_socket.close()
            print("[CLIENT] Đã đóng kết nối")

if __name__ == "__main__":
    client = Client()
    client.connect()
    client.send_message("Hello Server!")
    print("Server:", client.receive_message())
    client.close()
