import customtkinter as ctk
import sys
import os

# Đảm bảo project root trong sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from Client.Gui import ChatApp
    from Client.Login_gui import LoginGUI
except ImportError as e:    
    print(f"Import error: {e}")
    # Fallback: try direct import
    from Gui import ChatApp
    from Login_gui import LoginGUI

def main():
    print("🚀 Khởi động Chat Client với GUI...")

    def on_login_success(username):
        ctk.set_appearance_mode("light")
        root = ctk.CTk()
        root.title(f"Chat Application - {username}")
        root.geometry("1200x800")

        app = ChatApp(root, username=username)
        root.mainloop()

    login_app = LoginGUI(on_login_success_callback=on_login_success)
    login_app.show()

if __name__ == "__main__":
    main()