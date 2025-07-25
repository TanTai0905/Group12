import socket

def connect_to_server(host, port):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        print(f"✅ Connected to server at {host}:{port}")
        return client_socket
    except socket.error as e:
        print(f"❌ Error connecting to server: {e}")
        return None

def receive_message(sock):
    try:
        data = sock.recv(1024)
        if not data:
            return None
        return data.decode('utf-8').strip()
    except:
        return None

def send_message(sock, message):
    try:
        sock.send(message.encode('utf-8'))
    except:
        print(" Failed to send message.")

def main():
    host = "127.0.0.1"
    port = 12345
    client_socket = connect_to_server(host, port)

    if client_socket:
        # 1. Nhận lời chào từ server và yêu cầu nhập tên
        welcome = receive_message(client_socket)
        if welcome:
            print(f"\n📩 Server: {welcome}")
            name = input("👤 Your name: ")
            send_message(client_socket, name)

            # 2. Nhận hướng dẫn tiếp theo
            intro_msg = receive_message(client_socket)
            if intro_msg:
                print(f"📩 Server: {intro_msg}")

                while True:
                    guess = input("🎯 Enter your guess (or 'exit' to quit): ")
                    if guess.lower() == 'exit':
                        print("👋 Exiting game.")
                        break

                    send_message(client_socket, guess)
                    response = receive_message(client_socket)
                    if response:
                        print(f"📩 Server: {response}")
                        # Kết thúc nếu đoán đúng hoặc hết lượt
                        if "Correct!" in response or "Better luck" in response:
                            break
                    else:
                        print("⚠️ Disconnected from server.")
                        break

        client_socket.close()

if __name__ == "__main__":
    main()
