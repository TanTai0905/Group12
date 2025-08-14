import socket
import threading
import pyaudio
import time

class AudioStream:
    def __init__(self, host, port, chunk=1024, rate=44100, channels=1, callback=None):
        self.host = host
        self.port = port
        self.chunk = chunk
        self.rate = rate
        self.channels = channels
        self.callback = callback  # GUI sẽ nhận trạng thái từ đây
        self.running = False
        self.thread = None

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._stream_audio, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()

    def _stream_audio(self):
        audio = pyaudio.PyAudio()
        reconnect_delay = 3

        while self.running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((self.host, self.port))
                if self.callback:
                    self.callback("connected")

                stream = audio.open(format=pyaudio.paInt16,
                                    channels=self.channels,
                                    rate=self.rate,
                                    input=True,
                                    frames_per_buffer=self.chunk)

                while self.running:
                    data = stream.read(self.chunk, exception_on_overflow=False)
                    sock.sendall(data)

            except ConnectionRefusedError:
                if self.callback:
                    self.callback("server_not_responding")
                time.sleep(reconnect_delay)
            except (BrokenPipeError, ConnectionResetError):
                if self.callback:
                    self.callback("connection_lost")
                time.sleep(reconnect_delay)
            except Exception as e:
                if self.callback:
                    self.callback(f"error: {e}")
                time.sleep(reconnect_delay)
            finally:
                try:
                    stream.stop_stream()
                    stream.close()
                except:
                    pass
                try:
                    sock.close()
                except:
                    pass
