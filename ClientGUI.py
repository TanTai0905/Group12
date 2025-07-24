import tkinter as tk
import random
from PIL import  Image, ImageTk

# Tạo một số ngẫu nhiên từ 1 đến 100
secret_number = random.randint(1, 100)

# Hàm để xử lý khi người chơi nhấn nút "Gửi"
def check_guess():
    try:
        guess = int(entry.get())
        if guess < 1 or guess > 100:
            result_label.config(text="Số không hợp lệ! Vui lòng nhập số từ 1 đến 100.")
        elif guess < secret_number:
            result_label.config(text="Cao hơn!")
        elif guess > secret_number:
            result_label.config(text="Thấp hơn!")
        else:
            result_label.config(text="Chính xác! Bạn đã đoán đúng số!")
    except ValueError:
        result_label.config(text="Số không hợp lệ! Vui lòng nhập một số nguyên.")

# Tạo cửa sổ chính
root = tk.Tk()
root.title("Number guessing game")
root.geometry("1000x1000")
root.config(background = "white")
root.resizable(False, False)

# Thêm hình ảnh nền
background_image = Image.open("background.jpg")
background_image = background_image.resize((1000, 1000), Image.Resampling.LANCZOS)
bg_image = ImageTk.PhotoImage(background_image)

# Tạo một nhãn để đặt hình ảnh làm nền
background_label = tk.Label(root, image=bg_image)
background_label.place(relwidth=1, relheight=1)  # Đặt nhãn để lấp đầy cửa sổ

#
main_frame = tk.Frame(root, bg='white', bd=0, relief='flat')
main_frame.place(relx=0.5, rely=0.5, anchor='center')

# Tạo nhãn hướng dẫn
instruction_label = tk.Label(main_frame, text="Đoán một số từ 1 đến 100.", font = "arial 15 bold", fg = 'Red')
instruction_label.pack(pady=10)

# Tạo ô nhập liệu
entry = tk.Entry(main_frame, font = "arial 15", fg = 'black', bd = 4, width = 25, bg="white") # Hoặc màu khác bạn muốn
entry.pack(pady=10)

# Tạo nút bấm
submit_button = tk.Button(main_frame, text="Gửi", command=check_guess)
submit_button.pack(pady=10)

# Tạo khu vực hiển thị văn bản
result_label = tk.Label(main_frame, text="")
result_label.pack(pady=10)

# Bắt đầu vòng lặp chính
root.mainloop()
