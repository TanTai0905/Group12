import socket
import threading
import random

def generate_secret_number():
    """Generate a random secret number between 1 and 100."""
    return random.randint(1, 100)

def receive_message(client_socket):
    """Receive a message from the client."""
    data = client_socket.recv(1024).decode('utf-8')
    if not data:
        return None
    return data.strip()

def receive_guess(client_socket):
    """Receive and parse the guess from the client."""
    data = receive_message(client_socket)
    if data is None:
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
    ip, port = addr  # unpack IP and port
    print(f"[INFO] New connection from {ip}:{port}")

    send_message(client_socket, "Welcome! Please enter your name:")
    player_name = receive_message(client_socket)
    if not player_name:
        client_socket.close()
        return
    print(f"[INFO] Player '{player_name}' connected from {ip}:{port}")

    secret_number = generate_secret_number()
    print(f"[INFO] Secret number for {player_name} ({ip}:{port}): {secret_number}")

    max_attempts = 10
    attempts = 0

    send_message(client_socket, f"Hello {player_name}! Guess the secret number (1-100). You have {max_attempts} attempts.")

    while attempts < max_attempts:
        guess = receive_guess(client_socket)
        if guess is None:
            print(f"[INFO] {player_name} ({ip}:{port}) disconnected.")
            break
        if guess == "invalid":
            send_message(client_socket, "Please enter a valid number.")
            continue

        attempts += 1

        if guess < secret_number:
            if attempts < max_attempts:
                send_message(client_socket, f"Higher! Attempts left: {max_attempts - attempts}")
        elif guess > secret_number:
            if attempts < max_attempts:
                send_message(client_socket, f"Lower! Attempts left: {max_attempts - attempts}")
        else:
            send_message(client_socket, f"Correct! Congratulations {player_name}, you've guessed the number in {attempts} attempts.")
            print(f"[INFO] {player_name} ({ip}:{port}) guessed correctly!")
            break
    else:
        send_message(client_socket, f"You fail! The number was {secret_number}.")

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
    HOST = "127.0.0.1"
    PORT = 12345
    start_server(HOST, PORT)