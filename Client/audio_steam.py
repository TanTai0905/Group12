# audio_steam.py
import socket
import pyaudio
import time

# ===== CONFIG =====
SERVER_HOST = "0.0.0.0"  # Địa chỉ IP của server
SERVER_PORT = 50007 # Cổng kết nối tới server
CHUNK = 1024 
FORMAT = pyaudio.paInt16 
CHANNELS = 1
RATE = 44100
RECONNECT_DELAY = 3


def audio_stream():
    """Ghi âm từ mic và gửi tới server."""
    audio = pyaudio.PyAudio()

    while True:
        try:
            print(f"[AUDIO] Đang kết nối tới {SERVER_HOST}:{SERVER_PORT}...")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((SERVER_HOST, SERVER_PORT))
            print("[AUDIO] Đã kết nối tới server")

            stream = audio.open(format=FORMAT,
                                channels=CHANNELS,
                                rate=RATE,
                                input=True,
                                frames_per_buffer=CHUNK)

            while True:
                data = stream.read(CHUNK, exception_on_overflow=False)
                sock.sendall(data)

        except ConnectionRefusedError:
            print(f"[ERROR] Server không phản hồi, thử lại sau {RECONNECT_DELAY}s...")
            time.sleep(RECONNECT_DELAY)
        except (BrokenPipeError, ConnectionResetError):
            print("[ERROR] Mất kết nối tới server, đang thử lại...")
            time.sleep(RECONNECT_DELAY)
        except Exception as e:
            print(f"[ERROR] Lỗi không xác định: {e}")
            time.sleep(RECONNECT_DELAY)
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

if __name__ == "__main__":
    audio_stream()
