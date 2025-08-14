import customtkinter as ctk
from Gui import start_chat_app

def create_login_window():
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    
    root = ctk.CTk()
    root.title("Đăng Nhập")
    root.geometry("1000x600")
    
    # ------------------ Khung đăng nhập chính ------------------
    # Tăng kích thước và bo góc khung đăng nhập
    login_frame = ctk.CTkFrame(master=root, 
                               width=400, 
                               height=450,
                               corner_radius=20, 
                               fg_color=("white", "#2b2b2b"))
    login_frame.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

    # Tiêu đề "Đăng Nhập" lớn hơn và đậm hơn
    title_label = ctk.CTkLabel(master=login_frame, text="Đăng Nhập", font=("Arial", 36, "bold"), text_color=("black", "white"))
    title_label.pack(pady=40, padx=10)
    
    # Trường nhập Tên đăng nhập
    username_entry = ctk.CTkEntry(master=login_frame, 
                                  placeholder_text="Tên đăng nhập", 
                                  width=300, 
                                  height=50, # Chiều cao lớn hơn
                                  corner_radius=10,
                                  font=("Arial", 16))
    username_entry.pack(pady=15, padx=10)

    # Trường nhập Mật khẩu
    password_entry = ctk.CTkEntry(master=login_frame, 
                                  placeholder_text="Mật khẩu", 
                                  width=300, 
                                  height=50, # Chiều cao lớn hơn
                                  corner_radius=10,
                                  show="*",
                                  font=("Arial", 16))
    password_entry.pack(pady=15, padx=10)

    def on_login_clicked():
        username = username_entry.get()
        password = password_entry.get()
        if username and password:
            root.destroy()
            start_chat_app(username)
        else:
            username_entry.configure(placeholder_text="Nhập tên đăng nhập!", fg_color="red", border_color="red")
            password_entry.configure(placeholder_text="Nhập mật khẩu!", fg_color="red", border_color="red")
            
    # Nút Đăng Nhập
    login_button = ctk.CTkButton(master=login_frame, 
                                 text="Đăng Nhập", 
                                 command=on_login_clicked,
                                 width=300,
                                 height=50,
                                 corner_radius=10,
                                 font=("Arial", 18, "bold"))
    login_button.pack(pady=20, padx=10)

    root.mainloop()

if __name__ == "__main__":
    create_login_window()