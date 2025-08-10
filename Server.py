# main_server.py
import socket

class Server:
    def __init__(self, host="127.0.0.1", port=5001):
        self.host = host
        self.port = port
        self.server_socket = None

    def start(self):
        """Khởi tạo và chạy server."""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # === THÊM DÒNG NÀY VÀO ===
        # Cho phép tái sử dụng địa chỉ socket ngay lập tức
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.server_socket.bind((self.host, self.port))
            # ... (phần còn lại của code giữ nguyên)
            print(f"[SERVER] Đang lắng nghe trên {self.host}:{self.port}")
            
            self.server_socket.listen(1)
            
            while True:
                print("[SERVER] Đang chờ client kết nối...")
                conn, addr = self.server_socket.accept()
                print(f"[SERVER] Client {addr} đã kết nối.")
                
                with conn:
                    data = conn.recv(1024).decode()
                    if not data:
                        break
                    
                    print(f"Client ({addr}): {data}")
                    
                    response_msg = "Hello Client! Received your message."
                    conn.sendall(response_msg.encode())
                    print(f"[SERVER] Đã gửi phản hồi tới {addr}")

        except Exception as e:
            print(f"[ERROR] Có lỗi xảy ra: {e}")
        finally:
            self.close()

    def close(self):
        """Đóng socket của server."""
        if self.server_socket:
            self.server_socket.close()
            print("[SERVER] Đã đóng socket.")

if __name__ == "__main__":
    server = Server()
    server.start()