import socket
import threading

HOST = "0.0.0.0"  
PORT = 5001      

def handle_client(client_socket, client_address):
    """Xử lý kết nối từ một client."""
    print(f"[KẾT NỐI] Client {client_address} đã kết nối.")

    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break  # Client đóng kết nối
            message = data.decode('utf-8')
            print(f"[{client_address}] {message}")

            # Gửi lại phản hồi cho client (echo)
            client_socket.sendall(f"Server nhận: {message}".encode('utf-8'))

    except Exception as e:
        print(f"[LỖI] Client {client_address}: {e}")

    finally:
        client_socket.close()
        print(f"[NGẮT] Client {client_address} đã ngắt kết nối.")

def main():
    # Tạo socket TCP
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        print(f"[SERVER] Đang chạy tại {HOST}:{PORT} ...")

        while True:
            client_socket, client_address = server_socket.accept()
            # Tạo luồng riêng để xử lý client
            client_thread = threading.Thread(
                target=handle_client, 
                args=(client_socket, client_address),
                daemon=True
            )
            client_thread.start()

    except Exception as e:
        print(f"[LỖI] {e}")
    finally:
        server_socket.close()
        print("[SERVER] Đã tắt.")

if __name__ == "__main__":
    main()
