# Gui.py
import customtkinter as ctk
import threading
import json
from datetime import datetime
from .history_manager import HistoryManager
from .chat_handler import ChatHandler
from .audio_stream import AudioStream
from ..shared import config


class ChatApp:
    def __init__(self, root, username="User", host=config.HOST_CLIENT_CONNECT):
        self.root = root
        self.username = username
        self.host = host
        self.root.title(f"Ứng Dụng Chat - {username}")
        self.root.geometry("1000x700")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Lịch sử chat
        self.history_manager = HistoryManager()
        
        # Kết nối chat
        self.chat_handler = ChatHandler(
            host=self.host, 
            username=self.username,
            history_manager=self.history_manager
        )
        
        # Audio stream (sẽ được khởi tạo khi tham gia phòng)
        self.audio_stream = None
        self.current_room_id = None
        self.is_audio_connected = False
        
        # Giao diện
        self.setup_ui()
        
        # Kết nối chat server
        self.connect_chat_server()

    def setup_ui(self):
        # ===== Main frame =====
        main_frame = ctk.CTkFrame(master=self.root, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=3)
        main_frame.grid_rowconfigure(0, weight=1)

        # ===== Khung danh sách user và phòng =====
        self.sidebar_frame = ctk.CTkFrame(master=main_frame, width=200,
                                         corner_radius=10, fg_color="#3498db")
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.sidebar_frame.grid_rowconfigure(1, weight=1)
        
        # Tiêu đề sidebar
        sidebar_title = ctk.CTkLabel(self.sidebar_frame, text="Danh sách phòng & người dùng",
                                    font=("Arial", 16, "bold"), text_color="white")
        sidebar_title.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        # Khung chứa danh sách
        self.list_container = ctk.CTkScrollableFrame(self.sidebar_frame, fg_color="#2980b9")
        self.list_container.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        
        # Khung tạo/tham gia phòng
        self.room_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="#2980b9")
        self.room_frame.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        
        room_label = ctk.CTkLabel(self.room_frame, text="Tham gia phòng:", 
                                 text_color="white", font=("Arial", 12, "bold"))
        room_label.grid(row=0, column=0, columnspan=2, padx=5, pady=(5, 0), sticky="w")
        
        self.room_id_entry = ctk.CTkEntry(self.room_frame, placeholder_text="ID phòng")
        self.room_id_entry.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        
        self.room_password_entry = ctk.CTkEntry(self.room_frame, placeholder_text="Mật khẩu (nếu có)", show="*")
        self.room_password_entry.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        
        join_button = ctk.CTkButton(self.room_frame, text="Tham gia", 
                                   command=self.join_room, width=60,
                                   fg_color="#2ecc71", hover_color="#27ae60")
        join_button.grid(row=2, column=1, padx=5, pady=5)
        
        create_button = ctk.CTkButton(self.room_frame, text="Tạo phòng", 
                                     command=self.create_room, width=60,
                                     fg_color="#f39c12", hover_color="#e67e22")
        create_button.grid(row=1, column=1, padx=5, pady=5)
        
        leave_button = ctk.CTkButton(self.room_frame, text="Rời phòng", 
                                    command=self.leave_room, width=60,
                                    fg_color="#e74c3c", hover_color="#c0392b")
        leave_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

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
        self.message_input.bind("<Return>", lambda event: self.send_message())

        send_button = ctk.CTkButton(master=self.input_frame, text="Gửi",
                                   command=self.send_message, corner_radius=10,
                                   height=40, fg_color="#2ecc71")
        send_button.grid(row=0, column=1, padx=(0, 5), pady=10)

        self.is_muted = False
        self.mute_button = ctk.CTkButton(master=self.input_frame, text="Mute",
                                        fg_color="#e74c3c", command=self.toggle_mute,
                                        corner_radius=10, height=40)
        self.mute_button.grid(row=0, column=2, padx=0, pady=10)
        
        # Trạng thái kết nối
        self.status_label = ctk.CTkLabel(self.root, text="Đang kết nối...", 
                                        text_color="white", fg_color="#34495e",
                                        corner_radius=5)
        self.status_label.place(relx=0.5, rely=0.98, anchor="center")

    def connect_chat_server(self):
        """Kết nối tới server chat"""
        success, message = self.chat_handler.connect()
        if success:
            self.update_status("Đã kết nối chat server", "green")
            # Bắt đầu lắng nghe tin nhắn
            self.chat_handler.receive_messages(self.handle_received_message)
            # Tải lịch sử chat
            self.load_chat_history()
        else:
            self.update_status(f"Lỗi kết nối chat: {message}", "red")

    def join_room(self):
        """Tham gia phòng chat và audio"""
        room_id = self.room_id_entry.get().strip()
        password = self.room_password_entry.get().strip()
        
        if not room_id:
            self.update_status("Vui lòng nhập ID phòng", "orange")
            return
            
        # Tham gia phòng chat
        success, message = self.chat_handler.join_room(room_id, password)
        if success:
            self.update_status(f"Đang tham gia phòng {room_id}...", "blue")
            self.current_room_id = room_id
            
            # Tham gia phòng audio
            self.join_audio_room(room_id, password)
        else:
            self.update_status(f"Lỗi tham gia phòng: {message}", "red")

    def create_room(self):
        """Tạo phòng chat và audio mới"""
        password = self.room_password_entry.get().strip()
        
        # Tạo phòng audio (phòng chat sẽ được tạo tự động khi audio được tạo)
        self.join_audio_room(None, password, "CREATE")

    def leave_room(self):
        """Rời khỏi phòng hiện tại"""
        if self.current_room_id:
            # Rời phòng chat
            success, message = self.chat_handler.leave_room()
            if success:
                self.update_status(f"Đã rời phòng {self.current_room_id}", "blue")
            
            # Dừng audio stream
            if self.audio_stream:
                self.audio_stream.stop()
                self.audio_stream = None
                self.is_audio_connected = False
            # lưu lịch sử cuộc gọi
            if hasattr(self, 'call_start_time'):
                duration = (datetime.now() - self.call_start_time).total_seconds()
                duration_str = str(int(duration))
                self.history_manager.add_call_entry(self.current_room_id, duration_str)
        self.current_room_id = None
        self.clear_user_list()
            
    def join_audio_room(self, room_id, password, mode="JOIN"):
        """Tham gia hoặc tạo phòng audio"""
        if self.audio_stream:
            self.audio_stream.stop()
            
        self.audio_stream = AudioStream(
            host=self.host,
            port=config.PORT_AUDIO,
            mode=mode,
            username=self.username,
            room_id=room_id,
            password=password,
            callback=self.handle_audio_event
        )
        self.call_start_time = datetime.now() #ghi lại thời gian bắt đầu cuộc gọi
        self.audio_stream.start()
        self.is_audio_connected = True

    def send_message(self):
        """Gửi tin nhắn chat"""
        message = self.message_input.get().strip()
        if message:
            success, result = self.chat_handler.send_message(message)
            if success:
                self.message_input.delete(0, "end")
            else:
                self.update_status(f"Lỗi gửi tin nhắn: {result}", "red")

    def toggle_mute(self):
        """Bật/tắt chế độ mute microphone"""
        if not self.audio_stream:
            self.update_status("Chưa kết nối audio", "orange")
            return
            
        self.is_muted = not self.is_muted
        self.audio_stream.mute_control.toggle()
        
        if self.is_muted:
            self.mute_button.configure(text="Unmute", fg_color="#f39c12")
            self.update_status("Microphone đã tắt", "blue")
        else:
            self.mute_button.configure(text="Mute", fg_color="#e74c3c")
            self.update_status("Microphone đã bật", "green")

    def handle_received_message(self, message_data):
        """Xử lý tin nhắn nhận được từ server"""
        msg_type = message_data.get("type", "")
        
        if msg_type == "CHAT_MESSAGE":
            # Hiển thị tin nhắn chat
            sender = message_data.get("username", "Unknown")
            message = message_data.get("message", "")
            room_id = message_data.get("room_id", "")
            
            if room_id == self.current_room_id:
                self.display_message(sender, message)
                self.history_manager.add_chat_entry(sender, message)
                
        elif msg_type == "USER_LIST":
            # Cập nhật danh sách người dùng
            self.update_user_list(message_data.get("users", []))
            
        elif msg_type == "ERROR":
            self.update_status(f"Lỗi: {message_data.get('message', 'Unknown error')}", "red")
            
        elif msg_type == "INFO":
            self.update_status(message_data.get("message", ""), "blue")

    def handle_audio_event(self, event_data):
        """Xử lý sự kiện từ audio stream"""
        event_type = event_data.get("type", "")
        
        if event_type == "STATUS":
            self.update_status(event_data.get("message", ""), "green")
            
        elif event_type == "ERROR":
            self.update_status(f"Lỗi audio: {event_data.get('message', '')}", "red")
            
        elif event_type == "USER_LIST":
            self.update_user_list(event_data.get("users", []))

    def display_message(self, sender, message):
        """Hiển thị tin nhắn trong khung chat"""
        self.chat_display.configure(state="normal")
        
        # Định dạng tin nhắn
        timestamp = datetime.now().strftime("%H:%M")
        if sender == self.username:
            display_text = f"[{timestamp}] Bạn: {message}\n"
            tag = "self"
        else:
            display_text = f"[{timestamp}] {sender}: {message}\n"
            tag = "other"
        
        # Chèn tin nhắn
        self.chat_display.insert("end", display_text, tag)
        
        # Định dạng màu sắc
        self.chat_display.tag_config("self", foreground="blue")
        self.chat_display.tag_config("other", foreground="black")
        
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")  # Tự động scroll xuống cuối

    def update_user_list(self, users):
        """Cập nhật danh sách người dùng trong phòng"""
        self.clear_user_list()
        
        for user in users:
            user_label = ctk.CTkLabel(self.list_container, text=user,
                                     fg_color="#3498db", corner_radius=5,
                                     text_color="white", font=("Arial", 12))
            user_label.pack(fill="x", padx=5, pady=2)

    def clear_user_list(self):
        """Xóa danh sách người dùng hiện tại"""
        for widget in self.list_container.winfo_children():
            widget.destroy()

    def update_status(self, message, color):
        """Cập nhật trạng thái kết nối"""
        color_map = {
            "green": "#2ecc71",
            "red": "#e74c3c",
            "blue": "#3498db",
            "orange": "#f39c12"
        }
        
        self.status_label.configure(text=message, fg_color=color_map.get(color, "#34495e"))
        print(f"Status: {message}")  # For debugging

    def load_chat_history(self):
        """Tải lịch sử chat từ HistoryManager"""
        chat_history = self.history_manager.get_history("CHAT")
        for entry in chat_history:
            self.display_message(entry["sender"], entry["message"])

    def on_closing(self):
        """Xử lý khi đóng ứng dụng"""
        if self.audio_stream:
            self.audio_stream.stop()
            
        if self.chat_handler:
            self.chat_handler.close()
            
        self.root.destroy()


if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    root = ctk.CTk()
    app = ChatApp(root, username="DemoUser")
    root.mainloop()