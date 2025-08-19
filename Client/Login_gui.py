import customtkinter as ctk
from Gui import start_chat_app
import json
import os

USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

def register_user(username, password):
    users = load_users()
    if username in users:
        return False, "Tên đăng nhập đã tồn tại"
    users[username] = password
    save_users(users)
    return True, "Đăng ký thành công"

def authenticate_user(username, password):
    users = load_users()
    if username not in users:
        return False, "Tên đăng nhập không tồn tại"
    if users[username] != password:
        return False, "Mật khẩu không đúng"
    return True, "Đăng nhập thành công"

def create_login_window():
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    
    root = ctk.CTk()
    root.title("Đăng Nhập")
    root.geometry("1000x600")
    
    # ------------------ Khung đăng nhập chính ------------------
    login_frame = ctk.CTkFrame(master=root, width=400, height=520, corner_radius=20, fg_color=("white", "#2b2b2b"))
    login_frame.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

    title_label = ctk.CTkLabel(master=login_frame, text="Đăng Nhập", font=("Arial", 36, "bold"), text_color=("black", "white"))
    title_label.pack(pady=30, padx=10)
    
    username_entry = ctk.CTkEntry(master=login_frame, placeholder_text="Tên đăng nhập", width=300, height=50,
                                  corner_radius=10, font=("Arial", 16))
    username_entry.pack(pady=12, padx=10)

    # --- Ô nhập mật khẩu ---
    password_entry = ctk.CTkEntry(master=login_frame, placeholder_text="Mật khẩu", width=300, height=50,
                                  corner_radius=10, show="*", font=("Arial", 16))
    password_entry.pack(pady=(12,5), padx=10)

    def toggle_password():
        if show_password_var.get():
            password_entry.configure(show="")
        else:
            password_entry.configure(show="*")
    
    show_password_var = ctk.BooleanVar(value=False)
    show_password_checkbox = ctk.CTkCheckBox(
        master=login_frame,
        text="Hiện mật khẩu",
        variable=show_password_var,
        command=toggle_password,
        font=("Arial", 12),
        checkbox_width=16,
        checkbox_height=16
    )
    # căn phải dưới ô mật khẩu
    show_password_checkbox.pack(anchor="e", padx=20, pady=(0,12))

    # Nút Đăng Nhập
    login_button = ctk.CTkButton(master=login_frame, text="Đăng Nhập", command=lambda: on_login_clicked(),
                                 width=300, height=50, corner_radius=10, font=("Arial", 18, "bold"))
    login_button.pack(pady=15, padx=10)
    
    # Link đăng ký
    register_frame = ctk.CTkFrame(master=login_frame, fg_color="transparent", height=30)
    register_frame.pack(pady=8)
    
    text_part = ctk.CTkLabel(master=register_frame, text="Chưa có tài khoản? ", font=("Arial", 14),
                             text_color=("black", "white"))
    text_part.pack(side=ctk.LEFT)
    
    link_part = ctk.CTkLabel(master=register_frame, text="Đăng ký", font=("Arial", 14, "bold"),
                             text_color=("#1F6AA5", "#3B8ED0"), cursor="hand2")
    link_part.pack(side=ctk.LEFT)
    
    def on_enter(e):
        link_part.configure(text_color=("#0F4C75", "#2A7CC7"), font=("Arial", 14, "bold", "underline"))
    def on_leave(e):
        link_part.configure(text_color=("#1F6AA5", "#3B8ED0"), font=("Arial", 14, "bold"))
    link_part.bind("<Enter>", on_enter)
    link_part.bind("<Leave>", on_leave)

    # Khung chứa thông báo
    message_label = ctk.CTkLabel(master=login_frame, text="", font=("Arial", 14))
    message_label.pack(pady=5)

    def clear_message():
        message_label.configure(text="")
        username_entry.configure(border_color=("#3B8ED0", "#1F6AA5"))
        password_entry.configure(border_color=("#3B8ED0", "#1F6AA5"))

    def on_login_clicked():
        clear_message()
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        
        if not username or not password:
            message_label.configure(text="Vui lòng nhập đầy đủ thông tin!", text_color="red")
            if not username:
                username_entry.configure(border_color="red")
            if not password:
                password_entry.configure(border_color="red")
            return
        
        success, msg = authenticate_user(username, password)
        if success:
            root.destroy()
            start_chat_app(username)
        else:
            message_label.configure(text=msg, text_color="red")

    def open_register_window():
        register_window = ctk.CTkToplevel(root)
        register_window.title("Đăng Ký Tài Khoản")
        register_window.geometry("500x550")
        register_window.resizable(False, False)
        register_window.grab_set()
        
        register_frame = ctk.CTkFrame(master=register_window, width=400, height=480,
                                     corner_radius=20, fg_color=("white", "#2b2b2b"))
        register_frame.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

        title_label = ctk.CTkLabel(master=register_frame, text="Đăng Ký", font=("Arial", 30, "bold"),
                                   text_color=("black", "white"))
        title_label.pack(pady=25, padx=10)
        
        reg_username_entry = ctk.CTkEntry(master=register_frame, placeholder_text="Tên đăng nhập", width=300, height=50,
                                          corner_radius=10, font=("Arial", 16))
        reg_username_entry.pack(pady=12, padx=10)

        reg_password_entry = ctk.CTkEntry(master=register_frame, placeholder_text="Mật khẩu", width=300, height=50,
                                          corner_radius=10, show="*", font=("Arial", 16))
        reg_password_entry.pack(pady=(12,5), padx=10)

        reg_confirm_password_entry = ctk.CTkEntry(master=register_frame, placeholder_text="Nhập lại mật khẩu", width=300,
                                                  height=50, corner_radius=10, show="*", font=("Arial", 16))
        reg_confirm_password_entry.pack(pady=(12,5), padx=10)

        def toggle_reg_password():
            if reg_show_password_var.get():
                reg_password_entry.configure(show="")
                reg_confirm_password_entry.configure(show="")
            else:
                reg_password_entry.configure(show="*")
                reg_confirm_password_entry.configure(show="*")
        
        reg_show_password_var = ctk.BooleanVar(value=False)
        reg_show_password_checkbox = ctk.CTkCheckBox(
            master=register_frame,
            text="Hiện mật khẩu",
            variable=reg_show_password_var,
            command=toggle_reg_password,
            font=("Arial", 12),
            checkbox_width=16,
            checkbox_height=16
        )
        # căn phải dưới ô mật khẩu
        reg_show_password_checkbox.pack(anchor="e", padx=20, pady=(0,12))

        reg_message_label = ctk.CTkLabel(master=register_frame, text="", font=("Arial", 14))
        reg_message_label.pack(pady=5)

        def on_register_clicked():
            username = reg_username_entry.get().strip()
            password = reg_password_entry.get().strip()
            confirm_password = reg_confirm_password_entry.get().strip()
            
            if not username or not password or not confirm_password:
                reg_message_label.configure(text="Vui lòng nhập đầy đủ thông tin!", text_color="red")
                return
            if password != confirm_password:
                reg_message_label.configure(text="Mật khẩu không khớp!", text_color="red")
                return
            
            success, msg = register_user(username, password)
            reg_message_label.configure(text=msg, text_color="green" if success else "red")
            if success:
                register_window.after(1500, register_window.destroy)

        register_button = ctk.CTkButton(master=register_frame, text="Đăng Ký", command=on_register_clicked,
                                       width=300, height=50, corner_radius=10, font=("Arial", 18, "bold"))
        register_button.pack(pady=15, padx=10)

    link_part.bind("<Button-1>", lambda e: open_register_window())

    root.mainloop()

if __name__ == "__main__":
    create_login_window()
