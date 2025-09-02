# audio_stream.py
import socket, threading, pyaudio, time, json
from .mute_control import MuteControl
from shared import config

class AudioStream:
    def __init__(self, host, port,
                 mode="JOIN", username="User", room_id=None, password=None,
                 chunk=config.AUDIO_CHUNK, rate=config.AUDIO_RATE, channels=config.AUDIO_CHANNELS,
                 callback=None):
        self.host = host
        self.port = port
        self.mode = mode
        self.username = username
        self.room_id = room_id
        self.password = password
        self.chunk = chunk
        self.rate = rate
        self.channels = channels
        self.callback = callback

        self.running = False
        self.send_thread = None
        self.recv_thread = None
        self.sock = None
        self.mute_control = MuteControl()

    def _send_init_data(self):
        if self.mode == "CREATE":
            msg = f"CREATE|{self.username}|{self.password or ''}"
        else:
            msg = f"JOIN|{self.room_id}|{self.username}|{self.password or ''}"
        self.sock.sendall(msg.encode(config.ENCODING))

    def start(self):
        if self.running:
            return
        self.running = True

        def connect_loop():
            while self.running:
                try:
                    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.sock.settimeout(5)
                    self.sock.connect((self.host, self.port))
                    self.sock.settimeout(1)
                    self._send_init_data()

                    if self.callback:
                        self.callback({"type": "STATUS", "message": "connected"})

                    self.send_thread = threading.Thread(target=self._send_audio, daemon=True)
                    self.recv_thread = threading.Thread(target=self._recv_audio, daemon=True)
                    self.send_thread.start()
                    self.recv_thread.start()

                    while self.running and self.sock:
                        time.sleep(1)
                except Exception as e:
                    if self.callback:
                        self.callback({"type": "ERROR", "message": f"connect_error: {e}"})
                    time.sleep(3)
                finally:
                    if self.sock:
                        try: self.sock.close()
                        except: pass
                        self.sock = None

        threading.Thread(target=connect_loop, daemon=True).start()

    def stop(self):
        self.running = False
        if self.sock:
            try: self.sock.close()
            except: pass
            self.sock = None

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
                    time.sleep(0.1)
                    continue
                try:
                    data = stream.read(self.chunk, exception_on_overflow=False)
                    self.sock.sendall(data)
                except Exception as e:
                    if self.callback:
                        self.callback({"type": "ERROR", "message": f"send_audio_error: {e}"})
                    break
        finally:
            try: stream.stop_stream(); stream.close()
            except: pass
            audio.terminate()

    def _recv_audio(self):
        audio = pyaudio.PyAudio()
        try:
            stream = audio.open(format=pyaudio.paInt16,
                                channels=self.channels,
                                rate=self.rate,
                                output=True,
                                frames_per_buffer=self.chunk)

            while self.running and self.sock:
                try:
                    data = self.sock.recv(self.chunk * 8)
                    if not data: break

                    if data.startswith(b"SYS_MSG|"):
                        msg = json.loads(data[len("SYS_MSG|"):].decode(config.ENCODING))
                        if self.callback: self.callback(msg)
                    elif data.startswith(b"USER_LIST|"):
                        users = json.loads(data[len("USER_LIST|"):].decode(config.ENCODING))
                        if self.callback: self.callback({"type": "USER_LIST", "users": users})
                    else:
                        stream.write(data)
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.callback:
                        self.callback({"type": "ERROR", "message": f"recv_audio_error: {e}"})
                    break
        finally:
            try: stream.stop_stream(); stream.close()
            except: pass
            audio.terminate()
