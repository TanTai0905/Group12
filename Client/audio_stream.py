import socket
import threading
import pyaudio
import time
import json
import sys
import os
from .mute_control import MuteControl

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
        self.callback = callback

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
                    self.sock.settimeout(5)  # tránh connect treo
                    self.sock.connect((self.host, self.port))
                    self.sock.settimeout(1)  # recv có timeout để thoát nhanh khi stop
                    self._send_init_data()

                    if self.callback:
                        self.callback({"type": "STATUS", "message": "connected"})

                    # Thread gửi và nhận
                    self.send_thread = threading.Thread(target=self._send_audio, daemon=True)
                    self.recv_thread = threading.Thread(target=self._recv_audio, daemon=True)
                    self.send_thread.start()
                    self.recv_thread.start()

                    # Không join ở đây, để reconnect loop hoạt động
                    while self.running and self.sock:
                        time.sleep(1)

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
            self.sock = None

        # Join threads an toàn (không join chính thread hiện tại)
        current = threading.current_thread()
        if self.send_thread and self.send_thread.is_alive() and self.send_thread != current:
            self.send_thread.join(timeout=1)
        if self.recv_thread and self.recv_thread.is_alive() and self.recv_thread != current:
            self.recv_thread.join(timeout=1)

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

            while self.running:
                try:
                    data = self.sock.recv(self.chunk * 8)  # buffer lớn hơn chút
                    if not data:
                        break

                    # Kiểm tra message control
                    if data.startswith(b"SYS_MSG|"):
                        try:
                            msg = json.loads(data[len("SYS_MSG|"):].decode(config.ENCODING))
                            if self.callback:
                                self.callback(msg)
                        except Exception as e:
                            if self.callback:
                                self.callback({"type": "ERROR", "message": f"json_error: {e}"})
                    elif data.startswith(b"USER_LIST|"):
                        try:
                            users = json.loads(data[len("USER_LIST|"):].decode(config.ENCODING))
                            if self.callback:
                                self.callback(users)
                        except Exception as e:
                            if self.callback:
                                self.callback({"type": "ERROR", "message": f"userlist_error: {e}"})
                    else:
                        # Mặc định coi là audio
                        try:
                            stream.write(data)
                        except Exception as e:
                            if self.callback:
                                self.callback({"type": "ERROR", "message": f"play_audio_error: {e}"})
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.callback:
                        self.callback({"type": "ERROR", "message": f"recv_audio_error: {e}"})
                    break
        finally:
            try:
                stream.stop_stream()
                stream.close()
            except:
                pass
            audio.terminate()
