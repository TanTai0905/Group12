import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw
import socket
import threading
import os

SERVER_HOST = "0.0.0.0"
SERVER_PORT = 5001

class LoginApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Login")
        self.geometry("500x400")
        self.resizable(False, False)

        self.create_widgets()
        self.bind("<Configure>", self.on_resize)

    def create_widgets(self):
        # Canvas background
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        try:
            self.original_bg = Image.open("background.jpg")
            self.bg_image = ImageTk.PhotoImage(self.original_bg.resize((500, 400)))
            self.bg_item = self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw")
        except FileNotFoundError:
            self.canvas.configure(bg="#2c3e50")
            self.bg_item = None

        # Form container (semi-transparent)
        self.form_frame = tk.Frame(self.canvas, bg="#ffffff", bd=0)
        self.form_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Avatar (optional)
        try:
            avatar_img = Image.open("avatar.jpg").resize((80, 80), Image.LANCZOS)
            mask = Image.new("L", (80, 80), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, 80, 80), fill=255)
            avatar_img.putalpha(mask)
            self.avatar_photo = ImageTk.PhotoImage(avatar_img)
            avatar_label = tk.Label(self.form_frame, image=self.avatar_photo, bg="#ffffff")
            avatar_label.pack(pady=(10, 15))
        except FileNotFoundError:
            pass

        # Username input with icon
        user_frame = tk.Frame(self.form_frame, bg="#f2f2f2")
        user_frame.pack(pady=5, padx=15, fill="x")
        if os.path.exists("user.png"):
            user_icon_img = Image.open("user.png").resize((20, 20), Image.LANCZOS)
            self.user_icon = ImageTk.PhotoImage(user_icon_img)
            tk.Label(user_frame, image=self.user_icon, bg="#f2f2f2").pack(side="left", padx=8)
        self.username_entry = tk.Entry(user_frame, font=("Segoe UI", 11), bg="#f2f2f2", bd=0, relief="flat")
        self.username_entry.insert(0, "Username")
        self.username_entry.config(fg="grey")
        self.username_entry.bind("<FocusIn>", lambda e: self.clear_placeholder(self.username_entry, "Username"))
        self.username_entry.bind("<FocusOut>", lambda e: self.restore_placeholder(self.username_entry, "Username"))
        self.username_entry.pack(side="left", fill="x", expand=True, ipady=6)

        # Password input with icon
        pass_frame = tk.Frame(self.form_frame, bg="#f2f2f2")
        pass_frame.pack(pady=5, padx=15, fill="x")
        if os.path.exists("lock.png"):
            pass_icon_img = Image.open("lock.png").resize((20, 20), Image.LANCZOS)
            self.pass_icon = ImageTk.PhotoImage(pass_icon_img)
            tk.Label(pass_frame, image=self.pass_icon, bg="#f2f2f2").pack(side="left", padx=8)
        self.password_entry = tk.Entry(pass_frame, font=("Segoe UI", 11), bg="#f2f2f2", bd=0, relief="flat")
        self.password_entry.insert(0, "Password")
        self.password_entry.config(fg="grey")
        self.password_entry.bind("<FocusIn>", self.on_password_focus_in)
        self.password_entry.bind("<FocusOut>", self.on_password_focus_out)
        self.password_entry.pack(side="left", fill="x", expand=True, ipady=6)

        # Login button (gradient style simulated with bg color change on hover)
        self.login_btn = tk.Label(self.form_frame, text="Sign In", font=("Segoe UI", 12, "bold"),
                                  fg="white", bg="#e74c3c", width=20, height=2, cursor="hand2")
        self.login_btn.pack(pady=(15, 10))
        self.login_btn.bind("<Button-1>", lambda e: self.attempt_login())
        self.login_btn.bind("<Enter>", lambda e: self.login_btn.config(bg="#ff5733"))
        self.login_btn.bind("<Leave>", lambda e: self.login_btn.config(bg="#e74c3c"))

    def clear_placeholder(self, entry, text):
        if entry.get() == text:
            entry.delete(0, tk.END)
            entry.config(fg="black")

    def restore_placeholder(self, entry, text):
        if not entry.get():
            entry.insert(0, text)
            entry.config(fg="grey")

    def on_password_focus_in(self, event):
        if self.password_entry.get() == "Password":
            self.password_entry.delete(0, tk.END)
            self.password_entry.config(fg="black", show="*")

    def on_password_focus_out(self, event):
        if not self.password_entry.get():
            self.password_entry.insert(0, "Password")
            self.password_entry.config(fg="grey", show="")

    def on_resize(self, event):
        if self.bg_item:
            resized = self.original_bg.resize((self.winfo_width(), self.winfo_height()), Image.LANCZOS)
            self.bg_image = ImageTk.PhotoImage(resized)
            self.canvas.itemconfig(self.bg_item, image=self.bg_image)

    def attempt_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if not username or username == "Username" or not password or password == "Password":
            messagebox.showwarning("Warning", "Please enter both username and password.")
            return
        threading.Thread(target=self.login, args=(username, password), daemon=True).start()

    def login(self, username, password):
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((SERVER_HOST, SERVER_PORT))
            client_socket.sendall(f"{username}|{password}".encode("utf-8"))
            response = client_socket.recv(1024).decode("utf-8")
            if response == "SUCCESS":
                messagebox.showinfo("Success", "Login successful!")
                self.after(100, self.destroy)
            else:
                messagebox.showerror("Failed", "Invalid username or password.")
        except ConnectionRefusedError:
            messagebox.showerror("Error", "Cannot connect to server.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            if 'client_socket' in locals():
                client_socket.close()

if __name__ == "__main__":
    app = LoginApp()
    app.mainloop()
