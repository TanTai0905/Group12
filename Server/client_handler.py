# server/client_handler.py

import threading
from shared.config import BUFFER_SIZE, ENCODING


class ClientHandler(threading.Thread):
    """
    Lớp chịu trách nhiệm xử lý một client kết nối tới server.
    Mỗi client sẽ chạy trên một thread riêng biệt.
    """

    def __init__(self, client_socket, client_address):
        super().__init__(daemon=True)  # Chạy thread dạng nền
        self.client_socket = client_socket
        self.client_address = client_address
        self.active = True  # Đánh dấu trạng thái client còn kết nối

    def process_message(self, message: str) -> str:
        """
        Xử lý message nhận từ client.
        Hiện tại chỉ phản hồi echo, có thể mở rộng thêm chức năng sau này.
        """
        return f"Server nhận: {message}"

    def run(self):
        """Hàm chính được chạy khi thread start()."""
        print(f"[KẾT NỐI] Client {self.client_address} đã kết nối.")

        try:
            while self.active:
                data = self.client_socket.recv(BUFFER_SIZE)
                if not data:
                    break  # Client đã ngắt kết nối

                message = data.decode(ENCODING)
                print(f"[{self.client_address}] {message}")

                # Xử lý message và gửi lại phản hồi
                response = self.process_message(message)
                self.client_socket.sendall(response.encode(ENCODING))

        except ConnectionResetError:
            print(f"[LỖI] Client {self.client_address} ngắt đột ngột.")
        except Exception as e:
            print(f"[LỖI] Client {self.client_address}: {e}")
        finally:
            self.close()

    def close(self):
        """Đóng kết nối với client an toàn."""
        if self.active:
            self.active = False
            try:
                self.client_socket.close()
            except Exception:
                pass
            print(f"[NGẮT] Client {self.client_address} đã ngắt kết nối.")
