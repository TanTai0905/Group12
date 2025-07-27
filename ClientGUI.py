import socket
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

class GuessGame:
    def __init__(self, root):
        self.root = root
        self.root.title("🎯 Đoán Số")
        self.root.geometry("800x600")
        self.root.configure(bg="#ffffff")
        self.root.bind("<Configure>", self.resize_bg)

        self.socket = None
        self.bg_img = None
        self.load_background("background.jpg")

        # --- Giao diện nhập tên ---
        self.name_frame = tk.Frame(root, bg="#f6eed0")
        tk.Label(self.name_frame, text="Your name:", font=("Segoe UI", 20), bg="#f6eed0").pack(pady=10)
        self.name_entry = tk.Entry(self.name_frame, font=("Segoe UI", 12), width=30)
        self.name_entry.pack()
        tk.Button(self.name_frame, text="Start", command=self.start_game, width=30, height=2, bg="#C1CDCD", cursor="hand2").pack(pady=10)
        self.name_frame.pack(expand=True)

        # --- Khung chat ---
        self.text_frame = tk.Frame(root, bg="#ffffff", width=500, height=150)
        self.text_frame.pack_propagate(False)
        self.text = tk.Text(
            self.text_frame,
            height=8, width=60,
            font=("Segoe UI", 11),
            state="disabled", wrap="word",
            bg="#ffffff", relief="flat", bd=0
        )
        self.text.pack(padx=10, pady=5)

        # --- Nhập số đoán ---
        self.input_frame = tk.Frame(root, bg="#f6eed0")
        tk.Label(self.input_frame,text ="Enter a number:", font=("Segoe UI", 15), bg="#f6eed0").pack()
        self.guess_entry = tk.Entry(self.input_frame, width=10, font=("Segoe UI", 12))
        self.guess_entry.pack(side="left", padx=5)

        # --- Các nút điều khiển ---
        self.button_frame = tk.Frame(root,bg="#f6eed0")
        tk.Button(self.button_frame, text="Guess", command=self.send_guess,width=15, height=2, bg="#33FF33", cursor="hand2").pack(side="left", padx=10)
        tk.Button(self.button_frame, text="Reset", command=self.reset, width=15, height=2, bg="#FFFF33", cursor="hand2").pack(side="left", padx=10)
        tk.Button(self.button_frame, text="Exit", command=root.quit, width=15, height=2, bg="#FF0033", cursor="hand2").pack(side="left", padx=10)


    def resize_bg(self, e):
        if hasattr(self, "bg_original"):
            resized = self.bg_original.resize((e.width, e.height))
            self.bg_img = ImageTk.PhotoImage(resized)
            self.bg_label.config(image=self.bg_img)

    def start_game(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("⚠️", "Nhập tên trước khi chơi.")
            return
        self.name = name
        self.name_frame.pack_forget()

        self.text_frame.place(relx=0.5, rely=0.35, anchor="center")
        self.input_frame.place(relx=0.5, rely=0.55, anchor="center")
        self.button_frame.place(relx=0.5, rely=0.65, anchor="center")

        self.connect()

    def connect(self):
        try:
            self.socket = socket.socket()
            self.socket.connect(("127.0.0.1", 12345))
            self.display(self.recv())
            self.send(self.name)
            self.display(self.recv())
        except Exception as e:
            messagebox.showerror("Lỗi kết nối", str(e))

    def send_guess(self):
        guess = self.guess_entry.get().strip()
        if not guess:
            return
        self.send(guess)
        reply = self.recv()
        self.display("📩 " + reply)
        if "Chinh xac" in reply or "Ket thuc" in reply:
            self.socket.close()
            self.guess_entry.config(state="disabled")

    def reset(self):
        if self.socket:
            self.socket.close()
        self.guess_entry.config(state="normal")
        self.text.config(state="normal")
        self.text.delete(1.0, tk.END)
        self.text.config(state="disabled")
        self.connect()

    def send(self, msg):
        try:
            self.socket.send(msg.encode())
        except:
            self.display("❌ Không gửi được.")

    def recv(self):
        try:
            return self.socket.recv(1024).decode().strip()
        except:
            return ""

    def display(self, msg):
        self.text.config(state="normal")
        self.text.insert(tk.END, msg + "\n")
        self.text.config(state="disabled")
        self.text.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    GuessGame(root)
    root.mainloop()