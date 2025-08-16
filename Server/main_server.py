import socket
import threading
from shared.config import HOST_SERVER_BIND, PORT_CHAT, BUFFER_SIZE, ENCODING

def handle_client(client_socket, client_address):
    """Xử lý kết nối từ một client."""
    print(f"[KẾT NỐI] Client {client_address} đã kết nối.")

    try:
        while True:
            data = client_socket.recv(BUFFER_SIZE)
            if not data:
                break
            message = data.decode(ENCODING)
            print(f"[{client_address}] {message}")

            # Gửi lại phản hồi cho client (echo)
            client_socket.sendall(f"Server nhận: {message}".encode(ENCODING))

    except Exception as e:
        print(f"[LỖI] Client {client_address}: {e}")

    finally:
        client_socket.close()
        print(f"[NGẮT] Client {client_address} đã ngắt kết nối.")

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server_socket.bind((HOST_SERVER_BIND, PORT_CHAT))
        server_socket.listen(5)
        print(f"[SERVER] Đang chạy tại {HOST_SERVER_BIND}:{PORT_CHAT} ...")

        while True:
            client_socket, client_address = server_socket.accept()
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
