# server/main_server.py
import socket

def main():
    host = "0.0.0.0"  
    port = 5001      

    # Tạo socket TCP
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server_socket.bind((host, port))
        server_socket.listen(5)
        print(f"[SERVER] Đang chạy tại {host}:{port} ...")

        while True:
            client_socket, client_address = server_socket.accept()
            print(f"[KẾT NỐI] Client mới từ {client_address}")
            client_socket.close()  # Tạm thời đóng kết nối ngay (chưa xử lý gì)

    except Exception as e:
        print(f"[LỖI] {e}")
    finally:
        server_socket.close()
        print("[SERVER] Đã tắt.")

if __name__ == "__main__":
    main()
# 