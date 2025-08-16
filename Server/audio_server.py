import socket
import threading
import pyaudio
import time
from shared.config import HOST_CLIENT_CONNECT, PORT_CHAT, BUFFER_SIZE, ENCODING

class AudioServer:
    def __init__(self, callback=None):
        self.callback = callback  # Callback để cập nhật GUI
        self.running = False
        self.server_socket = None
        self.client_socket = None
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.thread = None

        # Audio config (có thể điều chỉnh theo client)
        self.chunk = BUFFER_SIZE  # Sử dụng BUFFER_SIZE từ config
        self.rate = 44100
        self.channels = 1
        self.format = pyaudio.paInt16

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._run_server, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        self._cleanup()

    def _cleanup(self):
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.client_socket:
            self.client_socket.close()
        if self.server_socket:
            self.server_socket.close()
        self.audio.terminate()

    def _run_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((HOST_SERVER, PORT_CHAT))  # Sử dụng config
        self.server_socket.listen(1)

        self._notify("SERVER_STARTED", f"Listening on {HOST_SERVER}:{PORT_CHAT}")

        while self.running:
            try:
                self.client_socket, addr = self.server_socket.accept()
                self._notify("CLIENT_CONNECTED", str(addr))

                self.stream = self.audio.open(
                    format=self.format,
                    channels=self.channels,
                    rate=self.rate,
                    output=True,
                    frames_per_buffer=self.chunk
                )

                while self.running:
                    try:
                        data = self.client_socket.recv(self.chunk)
                        if not data:
                            break
                        self.stream.write(data)
                    except ConnectionResetError:
                        self._notify("CLIENT_DISCONNECTED", "Connection reset")
                        break

            except Exception as e:
                self._notify("ERROR", str(e))
                time.sleep(1)
            finally:
                self._close_connections()

        self._cleanup()

    def _close_connections(self):
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
        if self.client_socket:
            self.client_socket.close()
            self.client_socket = None

    def _notify(self, event, message=""):
        if self.callback:
            self.callback(event, message)


# Cách sử dụng mẫu
if __name__ == "__main__":
    def status_handler(event, message):
        print(f"[{event}] {message}")

    server = AudioServer(callback=status_handler)
    
    try:
        server.start()
        print("Server đang chạy... Nhấn Ctrl+C để dừng")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server.stop()
        print("Server đã dừng")