# Realistic Number Guessing Game with Background, Music, Emoji, Stats, and Achievements
import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk
import random
import pyttsx3
import json
import os
import pygame

# Files for storing persistent data
LEADERBOARD_FILE = "leaderboard.json"
STATS_FILE = "stats.json"
ACHIEVEMENTS_FILE = "achievements.json"

class NumberGuessingGame:
    def __init__(self, master):
        self.master = master
        self.master.title("🎯 Real Number Guessing Game")
        self.master.geometry("1024x720")
        self.master.resizable(False, False)

        # Voice
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)

        # Welcome greeting based on time
        import datetime
        hour = datetime.datetime.now().hour
        if hour < 12:
            greeting = "Good morning!"
        elif hour < 18:
            greeting = "Good afternoon!"
        else:
            greeting = "Good evening!"
        messagebox.showinfo(
            "Welcome",
            f"{greeting} Welcome to the Real Number Guessing Game!\n\nCreated by Yuvan Shankar Raja\nGitHub: https://github.com/yuvanshankaraja"
        )

        # Background Music Setup
        pygame.mixer.init()
        music_file = "bg.mp3"
        if os.path.exists(music_file):
            try:
                pygame.mixer.music.load(music_file)
                pygame.mixer.music.set_volume(0.2)  # Minimal sound
                pygame.mixer.music.play(-1)
            except Exception as e:
                print(f"Error playing music: {e}")

        self.difficulty = tk.StringVar(value="Medium")
        self.max_range = 50
        self.max_attempts = 7
        self.remaining_attempts = 7
        self.score = 0
        self.number_to_guess = None

        self.stats = self.load_json(STATS_FILE, {
            "total_games": 0,
            "wins": 0,
            "perfect_wins": 0,
            "avg_score": 0.0,
            "last_score": 0
        })
        self.achievements = self.load_json(ACHIEVEMENTS_FILE, [])

        self.load_background()
        self.setup_ui()

    def load_background(self):
        try:
            if os.path.exists("bg.jpg"):
                bg_img = Image.open("bg.jpg")
            else:
                bg_img = Image.new('RGB', (1024, 720), 'white')  # Changed size to 1024x720
            bg_img = bg_img.resize((1024, 720))
            self.bg_img_tk = ImageTk.PhotoImage(bg_img)
            self.canvas = tk.Canvas(self.master, width=1024, height=720)
            self.canvas.pack(fill="both", expand=True)
            self.canvas.create_image(0, 0, image=self.bg_img_tk, anchor="nw")
        except Exception as e:
            print(f"Failed to load background image: {e}")
            self.canvas = tk.Canvas(self.master, width=1024, height=720, bg='white')  # Changed size to 1024x720
            self.canvas.pack(fill="both", expand=True)

    def setup_ui(self):
        # Center the emoji at the top
        self.emoji_label = tk.Label(self.master, text="🙂", font=("Arial", 40), bg='white')
        self.canvas.create_window(512, 60, window=self.emoji_label)  # Centered at top

        # Difficulty selection
        self.canvas.create_window(512, 140, window=tk.Label(self.master, text="Select Difficulty", font=("Arial", 12, "bold"), bg="white"))

        for i, (label, level) in enumerate([("Easy (1-10)", "Easy"), ("Medium (1-50)", "Medium"), ("Hard (1-100)", "Hard")]):
            self.canvas.create_window(512, 180 + i * 40, window=tk.Radiobutton(self.master, text=label, variable=self.difficulty, value=level, font=("Arial", 11), bg="white", padx=10, pady=5))

        # Start Game button
        self.canvas.create_window(512, 320, window=tk.Button(self.master, text="Start Game", command=self.start_game, font=("Arial", 12), width=16, pady=6))

        # Status label
        self.status_label = tk.Label(self.master, text="", font=("Arial", 12), bg="white")
        self.canvas.create_window(512, 370, window=self.status_label)

        # Entry for guess
        self.entry = tk.Entry(self.master, font=("Arial", 14), justify="center", width=10)
        self.entry.bind("<Return>", self.check_guess)
        self.canvas.create_window(512, 410, window=self.entry)

        # Check button
        self.check_btn = tk.Button(self.master, text="Check", command=self.check_guess, font=("Arial", 12), width=16, pady=6)
        self.canvas.create_window(512, 450, window=self.check_btn)

        # Score label
        self.score_label = tk.Label(self.master, text="Score: 0", font=("Arial", 12, "bold"), bg="white")
        self.canvas.create_window(512, 490, window=self.score_label)

        # Leaderboard button
        self.leaderboard_btn = tk.Button(self.master, text="Leaderboard", command=self.show_leaderboard, font=("Arial", 12), width=16, pady=6)
        self.canvas.create_window(512, 530, window=self.leaderboard_btn)

        # Next Round button, initially hidden
        self.next_round_btn = tk.Button(self.master, text="Next Round", command=self.start_next_round, font=("Arial", 12), width=16, pady=6)

    def load_json(self, path, default):
        if os.path.exists(path):
            with open(path, 'r') as f:
                return json.load(f)
        return default

    def save_json(self, path, data):
        with open(path, 'w') as f:
            json.dump(data, f, indent=4)

    def start_next_round(self):
        self.start_game()
        self.next_round_btn.place_forget()

    def start_game(self):
        self.status_label.config(text="Game started! Enter your guess.")
        self.entry.delete(0, tk.END)
        self.entry.config(state="normal")
        self.check_btn.config(state="normal")
        self.emoji_label.config(text="🙂")
        self.score_label.config(text=f"Score: {self.score}")
        # Set number to guess based on difficulty
        level = self.difficulty.get()
        if level == "Easy":
            self.max_range = 10
            self.max_attempts = 5
        elif level == "Medium":
            self.max_range = 50
            self.max_attempts = 7
        else:
            self.max_range = 100
            self.max_attempts = 10
        self.remaining_attempts = self.max_attempts
        self.number_to_guess = random.randint(1, self.max_range)
        self.status_label.config(text=f"Guess a number between 1 and {self.max_range}. Attempts left: {self.remaining_attempts}")

    def check_guess(self, event=None):
        guess = self.entry.get()
        try:
            guess = int(guess)
        except ValueError:
            self.status_label.config(text="Please enter a valid number.")
            return

        if guess == self.number_to_guess:
            self.status_label.config(text="Congratulations! You guessed the number!")
            self.emoji_label.config(text="🎉")
            self.score += 1
            self.score_label.config(text=f"Score: {self.score}")
            self.entry.config(state="disabled")
            self.check_btn.config(state="disabled")
            self.next_round_btn.place(x=200, y=450)  # Show next round button
        elif guess < self.number_to_guess:
            self.status_label.config(text="Too low! Try again.")
            self.emoji_label.config(text="😕")
        else:
            self.status_label.config(text="Too high! Try again.")
            self.emoji_label.config(text="😕")

        self.remaining_attempts -= 1
        if self.remaining_attempts <= 0 and guess != self.number_to_guess:
            self.status_label.config(text=f"Game over! The number was {self.number_to_guess}.")
            self.emoji_label.config(text="😢")
            self.entry.config(state="disabled")
            self.check_btn.config(state="disabled")
            self.next_round_btn.place(x=200, y=450)  # Show next round button

    def show_leaderboard(self):
        # Load leaderboard data
        leaderboard = self.load_json(LEADERBOARD_FILE, [])
        if not leaderboard:
            messagebox.showinfo("Leaderboard", "No scores yet!")
            return

        # Sort by score descending, then by name
        leaderboard_sorted = sorted(leaderboard, key=lambda x: (-x.get("score", 0), x.get("name", "")))
        top_entries = leaderboard_sorted[:10]

        leaderboard_text = "Top 10 Scores:\n\n"
        for idx, entry in enumerate(top_entries, 1):
            name = entry.get("name", "Anonymous")
            score = entry.get("score", 0)
            leaderboard_text += f"{idx}. {name}: {score}\n"

        messagebox.showinfo("Leaderboard", leaderboard_text)

if __name__ == "__main__":
    root = tk.Tk()
    game = NumberGuessingGame(root)
    root.mainloop()
