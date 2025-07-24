from tkinter import *
from tkinter import messagebox

# Tao cua so chinh
window = Tk()
window.title ("Number guessing game")
window.geometry ("1000x1000")

# Tieu de
lbl = Label (window, text="Xin mời bạn hãy nhập số đúng nhất", font=("Arial", 14))
lbl.pack()

window.mainloop()