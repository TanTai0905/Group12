import threading

BUFFER_SIZE = 1024  # Tạm đặt cố định ở đây

class ClientHandler(threading.Thread):
    def __init__(self, client_socket, client_address):
        super().__init__(daemon=True)  # Chạy thread dạng nền
        self.client_socket = client_socket
        self.client_address = client_address

    def run(self):
        """Hàm này sẽ chạy khi thread bắt đầu."""
        print(f"[CLIENT_HANDLER] Bắt đầu xử lý client: {self.client_address}")

        try:
            while True:
                data = self.client_socket.recv(BUFFER_SIZE)
                if not data:
                    break  # Client đã đóng kết nối
                print(f"[{self.client_address}] {data.decode('utf-8')}")
        except Exception as e:
            print(f"[LỖI] {self.client_address}: {e}")
        finally:
            self.client_socket.close()
            print(f"[CLIENT_HANDLER] Client {self.client_address} đã ngắt kết nối")
