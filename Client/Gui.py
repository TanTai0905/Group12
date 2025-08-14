import customtkinter as ctk
from PIL import Image, ImageTk, ImageFilter
from User_list import create_user_list_frame

class ChatApp:
    def __init__(self, root, username):
        self.root = root
        self.root.title(f"Ứng Dụng Chat - {username}")
        self.root.geometry("1000x700")

        # Khung chính chứa toàn bộ giao diện
        main_frame = ctk.CTkFrame(master=self.root, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=3)
        main_frame.grid_rowconfigure(0, weight=1)
        
        # Tạo khung danh sách người dùng với màu nổi bật
        self.user_list_frame = ctk.CTkFrame(master=main_frame, width=200, corner_radius=10, fg_color="#3498db") # Màu xanh dương
        self.user_list_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Khung chính của chat với màu nền sáng hơn
        self.main_chat_frame = ctk.CTkFrame(master=main_frame, corner_radius=10, fg_color="#ecf0f1") # Màu xám nhạt
        self.main_chat_frame.grid(row=0, column=1, sticky="nsew")
        self.main_chat_frame.grid_rowconfigure(0, weight=1)
        self.main_chat_frame.grid_rowconfigure(1, weight=0)
        self.main_chat_frame.grid_columnconfigure(0, weight=1)
        
        # Khung hiển thị tin nhắn chat
        self.chat_display = ctk.CTkTextbox(master=self.main_chat_frame, wrap="word", font=("Arial", 14), state="disabled", corner_radius=10, fg_color="white")
        self.chat_display.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="nsew")
        
        # Khung nhập tin nhắn và các nút
        self.input_frame = ctk.CTkFrame(master=self.main_chat_frame, corner_radius=10, fg_color="#bdc3c7") # Màu xám
        self.input_frame.grid(row=1, column=0, padx=10, pady=(5, 10), sticky="nsew")
        self.input_frame.grid_columnconfigure(0, weight=1)
        self.input_frame.grid_columnconfigure(1, weight=0)
        self.input_frame.grid_columnconfigure(2, weight=0)
        
        # Trường nhập tin nhắn
        self.message_input = ctk.CTkEntry(master=self.input_frame, placeholder_text="Nhập tin nhắn của bạn...", font=("Arial", 14), corner_radius=10, height=40, fg_color="white")
        self.message_input.grid(row=0, column=0, padx=(0, 10), pady=10, sticky="ew")
        
        # Nút gửi tin nhắn
        send_button = ctk.CTkButton(master=self.input_frame, text="Gửi", command=self.send_message, corner_radius=10, height=40, fg_color="#2ecc71") # Màu xanh lá
        send_button.grid(row=0, column=1, padx=(0, 5), pady=10)
        
        # Nút mute
        self.is_muted = False
        self.mute_button = ctk.CTkButton(master=self.input_frame, text="Mute", fg_color="#e74c3c", command=self.toggle_mute, corner_radius=10, height=40) # Màu đỏ
        self.mute_button.grid(row=0, column=2, padx=0, pady=10)
        
        # Gọi hàm tạo danh sách người dùng tại đây
        create_user_list_frame(self.user_list_frame)
        
    def send_message(self):
        message = self.message_input.get()
        if message and not self.is_muted:
            self.chat_display.configure(state="normal")
            self.chat_display.insert("end", f"Bạn: {message}\n")
            self.chat_display.configure(state="disabled")
            self.message_input.delete(0, "end")
            
    def toggle_mute(self):
        self.is_muted = not self.is_muted
        if self.is_muted:
            self.mute_button.configure(text="Unmute", fg_color="#f39c12") # Màu cam khi unmute
            self.message_input.configure(state="disabled")
            self.message_input.delete(0, "end")
        else:
            self.mute_button.configure(text="Mute", fg_color="#e74c3c") # Màu đỏ khi mute
            self.message_input.configure(state="normal")
            
def start_chat_app(username):
    root = ctk.CTk()
    ChatApp(root, username)
    root.mainloop()

if __name__ == "__main__":
    start_chat_app("DemoUser")