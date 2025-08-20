import socket
import threading
import pyaudio
import time
import json
from Client.mute_control import MuteControl
from shared import config


class AudioStream:
    def __init__(self, host, port,
                 mode="JOIN", username="User", room_id=None, password=None,
                 chunk=config.AUDIO_CHUNK, rate=config.AUDIO_RATE, channels=config.AUDIO_CHANNELS,
                 callback=None):
        """
        mode: "CREATE" hoặc "JOIN"
        username: tên user
        room_id: ID phòng (chỉ cần nếu JOIN)
        password: mật khẩu phòng (có thể None)
        callback: hàm callback(event hoặc message)
        """
        self.host = host
        self.port = port
        self.mode = mode
        self.username = username
        self.room_id = room_id
        self.password = password

        self.chunk = chunk
        self.rate = rate
        self.channels = channels
        self.callback = callback  # GUI nhận sự kiện từ đây

        self.running = False
        self.send_thread = None
        self.recv_thread = None
        self.sock = None
        self.mute_control = MuteControl()

    def _send_init_data(self):
        """Gửi thông tin tạo/join phòng"""
        if self.mode == "CREATE":
            msg = f"CREATE|{self.username}|{self.password or ''}"
        else:
            msg = f"JOIN|{self.room_id}|{self.username}|{self.password or ''}"
        self.sock.sendall(msg.encode(config.ENCODING))

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
                    self._send_init_data()  # gửi CREATE/JOIN tới server

                    if self.callback:
                        self.callback({"type": "STATUS", "message": "connected"})

                    # Thread gửi audio (mic → server)
                    self.send_thread = threading.Thread(target=self._send_audio, daemon=True)
                    self.recv_thread = threading.Thread(target=self._recv_audio, daemon=True)
                    self.send_thread.start()
                    self.recv_thread.start()

                    self.send_thread.join()
                    self.recv_thread.join()
                except Exception as e:
                    if self.callback:
                        self.callback({"type": "ERROR", "message": f"connect_error: {e}"})
                    time.sleep(3)  # thử lại sau 3s
                finally:
                    if self.sock:
                        try:
                            self.sock.close()
                        except:
                            pass
                        self.sock = None

        threading.Thread(target=connect_loop, daemon=True).start()

    def stop(self):
        """Dừng stream"""
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
        """Thu âm từ mic và gửi tới server"""
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
        """Nhận audio hoặc message từ server"""
        audio = pyaudio.PyAudio()
        try:
            stream = audio.open(format=pyaudio.paInt16,
                                channels=self.channels,
                                rate=self.rate,
                                output=True,
                                frames_per_buffer=self.chunk)
            buffer_size = self.chunk * 4  # đủ lớn để chứa JSON message
            while self.running:
                try:
                    data = self.sock.recv(buffer_size)
                    if not data:
                        break

                    # Kiểm tra nếu là message đặc biệt
                    if data.startswith(b"SYS_MSG|"):
                        msg = json.loads(data[len("SYS_MSG|"):].decode(config.ENCODING))
                        if self.callback:
                            self.callback(msg)
                    elif data.startswith(b"USER_LIST|"):
                        users = json.loads(data[len("USER_LIST|"):].decode(config.ENCODING))
                        if self.callback:
                            self.callback(users)
                    else:
                        # Mặc định coi là audio
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