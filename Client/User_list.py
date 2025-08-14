import customtkinter as ctk

def create_user_list_frame(parent_frame):
    label = ctk.CTkLabel(master=parent_frame, text="Người Dùng Online", font=("Arial", 16, "bold"), text_color="white")
    label.pack(pady=10, padx=10, anchor="n")
    
    users = ["Alice", "Bob", "Charlie", "David", "Eve"]
    
    for user in users:
        # Màu chữ trắng để nổi bật trên nền xanh
        user_label = ctk.CTkLabel(master=parent_frame, text=f"🟢 {user}", font=("Arial", 14), anchor="w", text_color="white")
        user_label.pack(fill="x", padx=15, pady=5)

if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()
    root.geometry("250x400")
    
    test_frame = ctk.CTkFrame(master=root, fg_color="#3498db")
    test_frame.pack(fill="both", expand=True)
    
    create_user_list_frame(test_frame)
    
    root.mainloop()