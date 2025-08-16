import socket
import threading
import select
import pyaudio
from shared.config import HOST_CLIENT_CONNECT, PORT_CHAT, BUFFER_SIZE, ENCODING

class ChatServer:
    def __init__(self):
        self.text_clients = []
        self.audio_clients = []
        self.running = False
        self.server_socket = None
        self.audio_stream = None
        self.audio = pyaudio.PyAudio()
        
        # Audio config
        self.chunk = BUFFER_SIZE
        self.rate = 44100
        self.channels = 1
        self.format = pyaudio.paInt16

    def start(self):
        self.running = True
        # Khởi tạo socket server cho text chat
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((HOST_SERVER, PORT_CHAT))
        self.server_socket.listen(5)
        
        print(f"Chat server đang chạy trên {HOST_SERVER}:{PORT_CHAT}")
        
        # Thread xử lý kết nối mới
        threading.Thread(target=self._accept_connections, daemon=True).start()

    def stop(self):
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        for client in self.text_clients + self.audio_clients:
            client.close()
        if self.audio:
            self.audio.terminate()

    def _accept_connections(self):
        while self.running:
            try:
                client_socket, addr = self.server_socket.accept()
                print(f"Kết nối mới từ {addr}")
                
                # Nhận loại kết nối (text/audio)
                conn_type = client_socket.recv(1024).decode(ENCODING)
                
                if conn_type == "TEXT":
                    self.text_clients.append(client_socket)
                    threading.Thread(
                        target=self._handle_text_client,
                        args=(client_socket,),
                        daemon=True
                    ).start()
                elif conn_type == "AUDIO":
                    self.audio_clients.append(client_socket)
                    if not self.audio_stream:
                        self._start_audio_stream()
            except Exception as e:
                print(f"Lỗi khi chấp nhận kết nối: {e}")

    def _handle_text_client(self, client_socket):
        try:
            while self.running:
                message = client_socket.recv(BUFFER_SIZE).decode(ENCODING)
                if not message:
                    break
                    
                print(f"Nhận tin nhắn: {message}")
                self._broadcast_text(message, client_socket)
        except Exception as e:
            print(f"Lỗi xử lý client: {e}")
        finally:
            self._remove_client(client_socket)

    def _broadcast_text(self, message, sender_socket):
        for client in self.text_clients:
            if client != sender_socket:
                try:
                    client.sendall(message.encode(ENCODING))
                except:
                    self._remove_client(client)

    def _start_audio_stream(self):
        self.audio_stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            output=True,
            frames_per_buffer=self.chunk,
            stream_callback=self._audio_callback
        )
        self.audio_stream.start_stream()

    def _audio_callback(self, in_data, frame_count, time_info, status):
        for client in self.audio_clients:
            try:
                client.sendall(in_data)
            except:
                self._remove_client(client)
        return (in_data, pyaudio.paContinue)

    def _remove_client(self, client_socket):
        if client_socket in self.text_clients:
            self.text_clients.remove(client_socket)
        if client_socket in self.audio_clients:
            self.audio_clients.remove(client_socket)
            if not self.audio_clients and self.audio_stream:
                self.audio_stream.stop_stream()
                self.audio_stream.close()
                self.audio_stream = None
        client_socket.close()


if __name__ == "__main__":
    server = ChatServer()
    try:
        server.start()
        while True:
            pass
    except KeyboardInterrupt:
        server.stop()
        print("Server đã dừng")