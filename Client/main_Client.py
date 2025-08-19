# Client/main_Client.py
from Client.audio_stream import AudioStream
from Client.chat_handler import ChatHandler
from Client.history_manager import HistoryManager
from shared import config

# Sau này sẽ thay bằng import GUI và Login_gui
# from Client.GUI import MainGUI
# from Client.Login_gui import LoginGUI

def main():
    print("🚀 Khởi động Client...")

    # Khởi tạo quản lý lịch sử
    history = HistoryManager()

    # Khởi tạo ChatHandler
    chat = ChatHandler(
        host=config.HOST_CLIENT_CONNECT,
        port=config.PORT_CHAT,
        username="UserTest"
    )
    ok, msg = chat.connect()
    print(msg)
    if not ok:
        return

    # Khởi tạo AudioStream
    audio = AudioStream(
        host=config.HOST_CLIENT_CONNECT,
        port=config.PORT_AUDIO,
        mode="JOIN",
        username="UserTest",
        room_id="general"
    )
    audio.start()

    # Fake callback demo (sau này GUI sẽ nhận sự kiện qua callback này)
    def chat_callback(data):
        print("[ChatCallback]", data)
        if data.get("type") == "CHAT_MESSAGE":
            history.add_chat_entry(data["username"], data["message"])

    chat.receive_messages(chat_callback)

    print("✅ Client đã sẵn sàng (chờ GUI/Login_gui tích hợp...)")

if __name__ == "__main__":
    main()
