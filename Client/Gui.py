# Gui.py
import customtkinter as ctk


class ChatApp:
    def __init__(self, root, username="User"):
        self.root = root
        self.root.title(f"Ứng Dụng Chat - {username}")
        self.root.geometry("1000x700")

        # ===== Main frame =====
        main_frame = ctk.CTkFrame(master=self.root, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=3)
        main_frame.grid_rowconfigure(0, weight=1)

        # ===== Khung danh sách user =====
        self.user_list_frame = ctk.CTkFrame(master=main_frame, width=200,
                                            corner_radius=10, fg_color="#3498db")
        self.user_list_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # Demo danh sách user
        self.demo_user_list()

        # ===== Khung chat chính =====
        self.main_chat_frame = ctk.CTkFrame(master=main_frame,
                                            corner_radius=10, fg_color="#ecf0f1")
        self.main_chat_frame.grid(row=0, column=1, sticky="nsew")
        self.main_chat_frame.grid_rowconfigure(0, weight=1)
        self.main_chat_frame.grid_rowconfigure(1, weight=0)
        self.main_chat_frame.grid_columnconfigure(0, weight=1)

        # Hiển thị tin nhắn
        self.chat_display = ctk.CTkTextbox(master=self.main_chat_frame, wrap="word",
                                           font=("Arial", 14), state="disabled",
                                           corner_radius=10, fg_color="white")
        self.chat_display.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="nsew")

        # ===== Khung nhập tin nhắn =====
        self.input_frame = ctk.CTkFrame(master=self.main_chat_frame, corner_radius=10,
                                        fg_color="#bdc3c7")
        self.input_frame.grid(row=1, column=0, padx=10, pady=(5, 10), sticky="nsew")
        self.input_frame.grid_columnconfigure(0, weight=1)
        self.input_frame.grid_columnconfigure(1, weight=0)
        self.input_frame.grid_columnconfigure(2, weight=0)

        self.message_input = ctk.CTkEntry(master=self.input_frame,
                                          placeholder_text="Nhập tin nhắn...",
                                          font=("Arial", 14), corner_radius=10,
                                          height=40, fg_color="white")
        self.message_input.grid(row=0, column=0, padx=(0, 10), pady=10, sticky="ew")

        send_button = ctk.CTkButton(master=self.input_frame, text="Gửi",
                                    command=self.send_message, corner_radius=10,
                                    height=40, fg_color="#2ecc71")
        send_button.grid(row=0, column=1, padx=(0, 5), pady=10)

        self.is_muted = False
        self.mute_button = ctk.CTkButton(master=self.input_frame, text="Mute",
                                         fg_color="#e74c3c", command=self.toggle_mute,
                                         corner_radius=10, height=40)
        self.mute_button.grid(row=0, column=2, padx=0, pady=10)

    def demo_user_list(self):
        """Tạo danh sách user demo"""
        demo_users = ["Alice", "Bob", "Charlie", "David"]
        for user in demo_users:
            btn = ctk.CTkButton(master=self.user_list_frame, text=user,
                                fg_color="#2980b9", hover_color="#1abc9c",
                                corner_radius=8)
            btn.pack(fill="x", padx=5, pady=5)

    def send_message(self):
        message = self.message_input.get()
        if message and not self.is_muted:
            self.chat_display.configure(state="normal")
            self.chat_display.insert("end", f"Bạn: {message}\n")
            self.chat_display.configure(state="disabled")
            self.chat_display.see("end")  # Tự động scroll xuống cuối
            self.message_input.delete(0, "end")

    def toggle_mute(self):
        self.is_muted = not self.is_muted
        if self.is_muted:
            self.mute_button.configure(text="Unmute", fg_color="#f39c12")
            self.message_input.configure(state="disabled")
            self.message_input.delete(0, "end")
        else:
            self.mute_button.configure(text="Mute", fg_color="#e74c3c")
            self.message_input.configure(state="normal")


if __name__ == "__main__":
    ctk.set_appearance_mode("light")  # hoặc "dark"
    root = ctk.CTk()
    app = ChatApp(root, username="DemoUser")
    root.mainloop()
