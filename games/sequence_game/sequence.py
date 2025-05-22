import tkinter as tk
from tkinter import ttk, messagebox
import random
import os
import time

BG_COLOR = "#ECF0F1"
TEXT_COLOR = "#2C3E50"
BUTTON_COLOR = "#0000FF"
ERROR_COLOR = "#E74C3C"
SUCCESS_COLOR = "#2ECC71"
ACCENT_COLOR = "#3498DB"

TITLE_FONT = ("Helvetica Neue", 28, "bold")
BODY_FONT = ("Helvetica Neue", 16)
SCORE_FONT = ("Helvetica Neue", 14)

HIGH_SCORE_FILE = "highscore.txt"


def generate_arithmetic_sequence():
    start = random.randint(1, 10)
    step = random.randint(1, 5)
    return [start + i * step for i in range(6)]

def generate_geometric_sequence():
    start = random.randint(1, 5)
    ratio = random.randint(2, 4)
    return [start * (ratio ** i) for i in range(6)]

def generate_fibonacci_sequence():
    seq = [random.randint(1, 5), random.randint(1, 5)]
    while len(seq) < 6:
        seq.append(seq[-1] + seq[-2])
    return seq

def insert_missing_values(sequence, count):
    indices = random.sample(range(len(sequence)), count)
    missing = {i: sequence[i] for i in indices}
    for i in indices:
        sequence[i] = '?'
    return sequence, missing

def get_sequence(difficulty):
    if difficulty == "easy":
        seq = generate_arithmetic_sequence()
        return insert_missing_values(seq, 1)
    elif difficulty == "medium":
        seq = generate_geometric_sequence()
        return insert_missing_values(seq, random.choice([1, 2]))
    elif difficulty == "hard":
        seq = generate_fibonacci_sequence()
        return insert_missing_values(seq, 2)


class LogicalGameApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sequence Logic Game with Timer Bar")
        self.root.geometry("640x560")
        self.root.configure(bg=BG_COLOR)

        self.score = 0
        self.high_score = self.load_high_score()
        self.fastest_time = None

        self.time_left = 15
        self.start_time = None
        self.timer_id = None
        self.progress = None

        self.current_difficulty = None
        self.sequence = []
        self.missing_values = {}
        self.entries = {}

        self.create_start_screen()

    def load_high_score(self):
        if os.path.exists(HIGH_SCORE_FILE):
            try:
                with open(HIGH_SCORE_FILE, "r") as file:
                    return int(file.read())
            except:
                return 0
        return 0

    def save_high_score(self):
        with open(HIGH_SCORE_FILE, "w") as file:
            file.write(str(self.high_score))

    def create_start_screen(self):
        self.clear_screen()

        tk.Label(self.root, text="Sequence Logic Game", font=TITLE_FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=30)
        tk.Label(self.root, text="Choose Difficulty:", font=BODY_FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=5)

        for diff in ["Easy", "Medium", "Hard"]:
            tk.Button(
                self.root, text=diff, font=BODY_FONT, width=14,
                bg=BUTTON_COLOR, fg="white", bd=0, activebackground=ACCENT_COLOR,
                command=lambda d=diff.lower(): self.start_game(d)
            ).pack(pady=8)

        tk.Label(self.root, text=f"Recent High Score: {self.high_score}", font=SCORE_FONT,
                 bg=BG_COLOR, fg=ACCENT_COLOR).pack(pady=10)

        if self.fastest_time:
            tk.Label(self.root, text=f"Fastest Answer: {self.fastest_time:.2f} sec", font=SCORE_FONT,
                     bg=BG_COLOR, fg=SUCCESS_COLOR).pack()

    def start_game(self, difficulty):
        self.current_difficulty = difficulty
        self.score = 0
        self.fastest_time = None
        self.new_round()

    def new_round(self):
        self.sequence, self.missing_values = get_sequence(self.current_difficulty)
        self.clear_screen()

        tk.Label(self.root, text=f"Difficulty: {self.current_difficulty.capitalize()}",
                 font=BODY_FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=5)

        tk.Label(self.root, text=f"Score: {self.score}", font=SCORE_FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack()
        tk.Label(self.root, text=f"High Score: {self.high_score}", font=SCORE_FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack()
        if self.fastest_time:
            tk.Label(self.root, text=f"Fastest Answer: {self.fastest_time:.2f} sec", font=SCORE_FONT,
                     bg=BG_COLOR, fg=SUCCESS_COLOR).pack()

        
        self.time_left = 15
        self.progress = ttk.Progressbar(self.root, maximum=15, length=400, mode="determinate")
        self.progress.pack(pady=10)
        self.progress['value'] = 0
        self.update_timer()

        display_seq = "   ".join(str(item) for item in self.sequence)
        tk.Label(self.root, text=display_seq, font=("Courier", 24), bg=BG_COLOR, fg=ACCENT_COLOR).pack(pady=15)

        self.entries = {}
        first_entry = None

        for idx in sorted(self.missing_values):
            frame = tk.Frame(self.root, bg=BG_COLOR)
            frame.pack(pady=5)
            tk.Label(frame, text=f"Missing #{idx + 1}:", font=BODY_FONT, bg=BG_COLOR, fg=TEXT_COLOR).pack(side=tk.LEFT)
            entry = tk.Entry(frame, width=6, font=BODY_FONT)
            entry.pack(side=tk.LEFT, padx=10)
            self.entries[idx] = entry
            if first_entry is None:
                first_entry = entry

        if first_entry:
            first_entry.focus_set()
            self.root.bind('<Return>', lambda e: self.check_answers())  # ⏎ to Submit

        tk.Button(self.root, text="Submit", font=BODY_FONT,
                  bg=BUTTON_COLOR, fg="white", bd=0, activebackground=ACCENT_COLOR,
                  command=self.check_answers).pack(pady=15)

        tk.Button(self.root, text="Quit", font=BODY_FONT,
                  bg=ERROR_COLOR, fg="white", bd=0,
                  command=self.root.quit).pack()

        self.start_time = time.time()

    def update_timer(self):
        if self.time_left > 0:
            self.time_left -= 1
            self.progress['value'] = 15 - self.time_left
            self.timer_id = self.root.after(1000, self.update_timer)
        else:
            self.progress['value'] = 15
            messagebox.showerror("Time Out!", f"⏰ You ran out of time!\nFinal Score: {self.score}")
            self.create_start_screen()

    def check_answers(self):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)

        correct = True
        for idx, entry in self.entries.items():
            try:
                value = int(entry.get())
                if value != self.missing_values[idx]:
                    correct = False
                    break
            except:
                correct = False
                break

        if correct:
            response_time = time.time() - self.start_time
            if self.fastest_time is None or response_time < self.fastest_time:
                self.fastest_time = response_time

            self.score += 1
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()

            
            self.new_round()
        else:
            messagebox.showerror("Wrong!", f" Game Over!\nFinal Score: {self.score}")
            self.create_start_screen()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.root.unbind('<Return>') 


if __name__ == "__main__":
    root = tk.Tk()
    app = LogicalGameApp(root)
    root.mainloop()
