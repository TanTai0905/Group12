import socket
import threading
import random

def generate_secret_number():
    """Generate a random secret number between 1 and 100."""
    return random.randint(1, 100)

def receive_guess(client_socket):
    """Receive and parse the guess from the client."""
    data = client_socket.recv(1024).decode('utf-8')
    if not data:
        return None
    try:
        return int(data)
    except ValueError:
        return "invalid"

def send_message(client_socket, message):
    """Send a message to the client."""
    client_socket.send(message.encode('utf-8'))

def handle_client(client_socket, addr):
    """Handle a single client session."""
    secret_number = generate_secret_number()
    print(f"[{addr}] Secret number: {secret_number}")

    while True:
        guess = receive_guess(client_socket)
        if guess is None:
            print(f"[{addr}] Disconnected.")
            break
        if guess == "invalid":
            send_message(client_socket, "Please enter a valid number.")
            continue

        if guess < secret_number:
            send_message(client_socket, "Higher! Try again.")
        elif guess > secret_number:
            send_message(client_socket, "Lower! Try again.")
        else:
            send_message(client_socket, "Correct! You've guessed the number.")
            print(f"[{addr}] Guessed correctly!")
            break

    client_socket.close()

def start_server(host, port):
    """Start the server and accept incoming connections."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f"Server listening on {host}:{port}")

    while True:
        client_socket, addr = server.accept()
        print(f"Accepted connection from {addr}")
        thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        thread.start()

if __name__ == "__main__":
    HOST = "0.0.0.0"
    PORT = 12345  # Specify a port number here
    start_server(HOST, PORT)