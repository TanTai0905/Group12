from Client.chat_handler import ChatHandler
from Client.audio_stream import AudioStream
from shared import config
import time

def main():
    # Tạo chat handler
    chat = ChatHandler(username="Tai")
    ok, msg = chat.connect()
    print(msg)
    if ok:
        chat.join_room("general")
        chat.receive_messages(lambda m: print("📩", m))

    # Tạo audio stream
    audio = AudioStream(host=config.HOST_CLIENT_CONNECT, port=config.PORT_AUDIO)
    audio.start()

    try:
        while True:
            cmd = input("Nhập tin nhắn (/quit để thoát): ")
            if cmd == "/quit":
                break
            chat.send_message(cmd)
    except KeyboardInterrupt:
        pass
    finally:
        chat.leave_room()
        chat.close()
        audio.stop()

if __name__ == "__main__":
    main()
