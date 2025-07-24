import tkinter as tk
from tkinter import messagebox

def submit():
    name = entry.get()
    messagebox.showinfo("Thông báo", f"Xin chào, {name}!")

root = tk.Tk()
root.title("Form Đơn Giản")

tk.Label(root, text="Nhập tên của bạn:").pack(pady=5)
entry = tk.Entry(root)
entry.pack(pady=5)

tk.Button(root, text="Gửi", command=submit).pack(pady=10)

root.mainloop()