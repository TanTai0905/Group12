import tkinter as tk
from tkinter import messagebox
import random
from PIL import Image, ImageTk

class GameApp:
    def __init__(self, master):
        self.master = master
        master.title("Guessing Game")
        
        # Thiết lập kích thước cửa sổ chính
        self.window_width = 650
        self.window_height =750
        master.geometry(f"{self.window_width}x{self.window_height}")
        master.minsize(550, 650)  # Kích thước tối thiểu
        
        # Tải hình nền và điều chỉnh kích thước
        try:
            self.bg_image = Image.open("background.webp")
            self.bg_image = self.bg_image.resize((self.window_width, self.window_height), Image.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(self.bg_image)
            self.background_label = tk.Label(master, image=self.bg_photo)
            self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
        except:
            master.configure(bg="#f0f0f0")
        
        # Biến trạng thái
        self.player_name = None
        self.secret_number = None
        self.attempts_left = 0
        
        # Tạo frame chính - điều chỉnh padding và kích thước
        self.main_frame = tk.Frame(master, 
                                  bg="white", 
                                  padx=25, 
                                  pady=25,
                                  width=int(self.window_width*0.9),
                                  height=int(self.window_height*0.9))
        self.main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.main_frame.pack_propagate(False)  # Ngăn frame co lại theo nội dung
        
        # Phần nhập tên
        self.create_name_input()
        
        # Phần game
        self.create_game_interface()
        self.hide_game_interface()
    
    def create_name_input(self):
        """Giao diện nhập tên với kích thước được điều chỉnh"""
        self.name_frame = tk.Frame(self.main_frame, bg="white")
        self.name_frame.pack(expand=True, pady=(0, 20))
        
        # Tiêu đề lớn hơn
        self.label_name = tk.Label(self.name_frame, 
                                  text="Welcome to Guessing Game!", 
                                  font=("Arial", 16, "bold"), 
                                  bg="white", fg="#333")
        self.label_name.pack(pady=15)
        
        # Ô nhập tên lớn hơn
        self.label_instruction = tk.Label(self.name_frame, 
                                         text="Please enter your name to start:",
                                         bg="white", fg="#555",
                                         font=("Arial", 11))
        self.label_instruction.pack()
        
        self.entry_name = tk.Entry(self.name_frame, 
                                  width=25, 
                                  font=("Arial", 12),
                                  bd=2, relief=tk.GROOVE)
        self.entry_name.pack(pady=15, ipady=7)
        
        # Nút Start lớn hơn
        self.button_start = tk.Button(self.name_frame, 
                                    text="Start Game", 
                                    command=self.start_game,
                                    bg="#4CAF50", fg="white",
                                    padx=20, pady=8,
                                    font=("Arial", 12, "bold"),
                                    bd=0)
        self.button_start.pack()
    
    def create_game_interface(self):
        """Tạo giao diện chơi game với các kích thước được chỉnh"""
        # Output area chiếm 60% chiều cao frame chính
        output_height = int(self.window_height * 0.6 / 15) 
        
        self.output_frame = tk.Frame(self.main_frame, bg="white")
        self.output_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        scrollbar = tk.Scrollbar(self.output_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.output_area = tk.Text(self.output_frame, 
                                 height=output_height,
                                 width=50, 
                                 yscrollcommand=scrollbar.set,
                                 bg="#f9f9f9", 
                                 fg="#333",
                                 font=("Arial", 10),
                                 padx=15, pady=15,
                                 wrap=tk.WORD,
                                 bd=2, relief=tk.GROOVE)
        self.output_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.output_area.yview)
        
        # Khu vực nhập liệu
        self.input_frame = tk.Frame(self.main_frame, bg="white")
        self.input_frame.pack(fill=tk.X, pady=10)
        
        self.label_guess = tk.Label(self.input_frame, 
                                   text="Enter your guess (1-100):",
                                   bg="white", fg="#555",
                                   font=("Arial", 11))
        self.label_guess.pack(side=tk.LEFT, padx=(0, 10))
        
        self.entry_guess = tk.Entry(self.input_frame, 
                                   width=8, 
                                   font=("Arial", 12),
                                   justify=tk.CENTER,
                                   bd=2, relief=tk.GROOVE)
        self.entry_guess.pack(side=tk.LEFT, ipady=5)
        
        # Frame nút chức năng - chiều rộng đầy đủ
        self.button_frame = tk.Frame(self.main_frame, bg="white")
        self.button_frame.pack(fill=tk.X, pady=10)
        
        # Style chung cho các nút
        button_style = {
            "padx": 20,
            "pady": 8,
            "font": ("Arial", 11, "bold"),
            "bd": 0
        }
        
        self.button_guess = tk.Button(self.button_frame, 
                                    text="Submit Guess", 
                                    command=self.submit_guess,
                                    bg="#2196F3", fg="white",
                                    **button_style)
        self.button_guess.pack(side=tk.LEFT, expand=True)
        
        self.button_reset = tk.Button(self.button_frame, 
                                    text="Reset Game", 
                                    command=self.reset_game,
                                    bg="#FF9800", fg="white",
                                    **button_style)
        self.button_reset.pack(side=tk.LEFT, expand=True, padx=10)
        
        self.button_exit = tk.Button(self.button_frame, 
                                   text="Exit", 
                                   command=self.exit_game,
                                   bg="#F44336", fg="white",
                                   **button_style)
        self.button_exit.pack(side=tk.LEFT, expand=True)
    
    def hide_game_interface(self):
        self.output_frame.pack_forget()
        self.input_frame.pack_forget()
        self.button_frame.pack_forget()
        
    def show_game_interface(self):
        self.output_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        self.input_frame.pack(fill=tk.X, pady=10)
        self.button_frame.pack(fill=tk.X, pady=10)
        
    def start_game(self):
        name = self.entry_name.get().strip()
        if not name:
            messagebox.showwarning("Input Error", "Please enter your name.")
            return
            
        self.player_name = name
        self.secret_number = random.randint(1, 100)
        self.attempts_left = 10
        
        self.name_frame.pack_forget()
        self.show_game_interface()
        
        self.output_area.configure(state='normal')
        self.output_area.delete(1.0, tk.END)
        welcome_msg = f"✨ Hello {self.player_name}!\n\n"
        welcome_msg += f"🔍 I'm thinking of a number between 1 and 100.\n"
        welcome_msg += f"🎯 You have {self.attempts_left} attempts to guess it.\n\n"
        welcome_msg += "💡 Type your guess and press 'Submit Guess'!"
        self.output_area.insert(tk.END, welcome_msg)
        self.output_area.configure(state='disabled')
        self.entry_guess.focus_set()
        
    def submit_guess(self):
        if self.secret_number is None:
            return
            
        guess = self.entry_guess.get().strip()
        self.entry_guess.delete(0, tk.END)
        
        try:
            guess = int(guess)
            if guess < 1 or guess > 100:
                raise ValueError("Out of range")
        except ValueError:
            self.display_message("⚠️ Please enter a valid number between 1 and 100.")
            return
            
        self.attempts_left -= 1
        self.output_area.configure(state='normal')
        
        if guess < self.secret_number:
            self.display_message(f"🔺 Your guess {guess} is too low! Try higher.")
        elif guess > self.secret_number:
            self.display_message(f"🔻 Your guess {guess} is too high! Try lower.")
        else:
            self.display_message(f"\n🎉 Congratulations {self.player_name}!\n\n"
                               f"🏆 You guessed the number {self.secret_number} correctly!\n"
                               f"⏳ You used {10 - self.attempts_left} attempts.\n\n"
                               f"Press 'Reset Game' to play again!")
            self.secret_number = None
            return
            
        if self.attempts_left <= 0:
            self.display_message(f"\n💔 Game Over!\n\n" 
                               f"🔢 The secret number was {self.secret_number}.\n\n"
                               f"🍀 Better luck next time!\n\n"
                               f"Press 'Reset Game' to try again!")
            self.secret_number = None
        else:
            self.display_message(f"\n💡 Attempts remaining: {self.attempts_left}")
            
        self.output_area.configure(state='disabled')
        
    def display_message(self, message):
        self.output_area.insert(tk.END, message + "\n")
        self.output_area.see(tk.END)
        
    def reset_game(self):
        if self.player_name:
            self.show_game_interface()
            self.start_game()
        else:
            messagebox.showinfo("Information", "Please enter your name first.")
            self.name_frame.pack(pady=20)
            self.hide_game_interface()
            self.entry_name.focus_set()
            
    def exit_game(self):
        if messagebox.askokcancel("Quit Game", "Are you sure you want to quit the game?"):
            self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    try:
        root.iconbitmap("game_icon.ico")
    except:
        pass
    app = GameApp(root)
    root.mainloop()
