import socket
import threading
import pyaudio
import time
from Client.mute_control import MuteControl
from shared import config

class AudioStream:
    def __init__(self, host, port, chunk=1024, rate=44100, channels=1, callback=None):
        self.host = host
        self.port = port
        self.chunk = chunk
        self.rate = rate
        self.channels = channels
        self.callback = callback  # GUI nhận trạng thái từ đây
        self.running = False
        self.send_thread = None
        self.recv_thread = None
        self.sock = None
        self.mute_control = MuteControl()

    def start(self):
        """Kết nối tới server audio và khởi chạy 2 luồng gửi/nhận"""
        if self.running:
            return
        self.running = True

        def connect_loop():
            while self.running:
                try:
                    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.sock.connect((self.host, self.port))
                    if self.callback: 
                        self.callback("connected")

                    # khi kết nối thành công thì chạy send/recv
                    self.send_thread = threading.Thread(target=self._send_audio, daemon=True)
                    self.recv_thread = threading.Thread(target=self._recv_audio, daemon=True)
                    self.send_thread.start()
                    self.recv_thread.start()
                    self.send_thread.join()
                    self.recv_thread.join()
                except Exception as e:
                    if self.callback: 
                        self.callback(f"connect_error: {e}")
                    time.sleep(3)  # thử lại sau 3s
                finally:
                    if self.sock:
                        try: self.sock.close()
                        except: pass
                        self.sock = None

        threading.Thread(target=connect_loop, daemon=True).start()

    def stop(self):
        self.running = False
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
        if self.send_thread:
            self.send_thread.join()
        if self.recv_thread:
            self.recv_thread.join()

    def _send_audio(self):
        audio = pyaudio.PyAudio()
        try:
            stream = audio.open(format=pyaudio.paInt16,
                                channels=self.channels,
                                rate=self.rate,
                                input=True,
                                frames_per_buffer=self.chunk)
            while self.running:
                if self.mute_control.get_status():
                    # Nếu đang mute thì bỏ qua gửi
                    time.sleep(0.1)
                    continue
                data = stream.read(self.chunk, exception_on_overflow=False)
                try:
                    self.sock.sendall(data)
                except:
                    break
        finally:
            try:
                stream.stop_stream()
                stream.close()
            except:
                pass
            audio.terminate()

    def _recv_audio(self):
        audio = pyaudio.PyAudio()
        try:
            stream = audio.open(format=pyaudio.paInt16,
                                channels=self.channels,
                                rate=self.rate,
                                output=True,
                                frames_per_buffer=self.chunk)
            while self.running:
                try:
                    data = self.sock.recv(self.chunk)
                    if not data:
                        break
                    stream.write(data)
                except:
                    break
        finally:
            try:
                stream.stop_stream()
                stream.close()
            except:
                pass
            audio.terminate()
