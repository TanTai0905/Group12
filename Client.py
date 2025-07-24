import socket

def connect_to_server(host, port):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        print(f"Connected to server at {host}:{port}")
        return client_socket
    except socket.error as e:
        print(f"Error connecting to server: {e}")
        return None

def send_guess(client_socket, guess):
    try:
        client_socket.sendall(guess.encode())
        response = client_socket.recv(1024).decode()
        return response
    except socket.error as e:
        print(f"Error sending guess: {e}")
        return None

def main():
    host = "127.0.0.1"
    port = 12345
    client_socket = connect_to_server(host, port)
    if client_socket:
        while True:
            guess = input("Enter your guess (or 'exit' to quit): ")
            if guess.lower() == 'exit':
                break
            response = send_guess(client_socket, guess)
            if response:
                print(f"Server response: {response}")
        client_socket.close()

if __name__ == "__main__":
    main()
