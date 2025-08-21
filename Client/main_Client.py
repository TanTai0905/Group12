import customtkinter as ctk
import sys
import os

# Thêm đường dẫn gốc và các thư mục cần thiết vào sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
sys.path.append(current_dir)

from Client.Gui import ChatApp
from Client.Login_gui import LoginGUI

def main():
    print("🚀 Khởi động Chat Client với GUI...")
    print(f"Current directory: {current_dir}")
    print(f"Parent directory: {parent_dir}")
    print(f"Python path: {sys.path}")

    def on_login_success(username):
        """Callback khi đăng nhập thành công"""
        ctk.set_appearance_mode("light")
        root = ctk.CTk()
        root.title(f"Chat Application - {username}")
        root.geometry("1200x800")

        app = ChatApp(root, username=username)
        root.mainloop()

    # Hiển thị màn hình đăng nhập đầu tiên
    login_app = LoginGUI(on_login_success_callback=on_login_success)
    login_app.show()

if __name__ == "__main__":
    main()