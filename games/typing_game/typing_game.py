import pygame
import random
import time
import sys
import json
from datetime import datetime

# Load leaderboard from JSON file
def load_leaderboard(filename="leaderboard.json"):
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Save leaderboard to JSON file
def save_leaderboard(data, filename="leaderboard.json"):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

leaderboard = load_leaderboard()

# Initialize Pygame
pygame.init()

# Fullscreen setup
infoObject = pygame.display.Info()
WIDTH, HEIGHT = infoObject.current_w, infoObject.current_h
win = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("TYPING GAME")

# Fonts
FONT = pygame.font.SysFont(['San Francisco', 'Helvetica Neue', 'Arial', 'sans-serif'], 42)
BIG_FONT = pygame.font.SysFont(['San Francisco', 'Helvetica Neue', 'Arial', 'sans-serif'], 150, bold=True)
TITLE_FONT = pygame.font.SysFont(['San Francisco', 'Helvetica Neue', 'Arial', 'sans-serif'], 80, bold=True)

# Colors
WHITE = (236, 240, 241)
BLUE = (52, 152, 219)
BUTTON_COLOR = (173, 216, 230)
BUTTON_HOVER = (135, 206, 250)

# Word list
words = [
    "hello", "world", "python", "cool", "keyboard", "speed", "test", "typing",
    "game", "program", "random", "screen", "timer", "score", "player", "learning",
    "awesome", "challenge", "solution", "function", "variable", "loop", "condition",
    "syntax", "statement", "indentation", "object", "class", "method", "module"
]

# Draw text
def draw_text(text, font, color, surface, x, y):
    render = font.render(text, True, color)
    surface.blit(render, (x, y))

def draw_centered_text(text, font, color, surface, center_x, center_y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(center_x, center_y))
    surface.blit(text_surface, text_rect)

def draw_button(text, x, y, w, h, surface, mouse_pos):
    is_hovered = x < mouse_pos[0] < x + w and y < mouse_pos[1] < y + h
    color = BUTTON_HOVER if is_hovered else BUTTON_COLOR
    pygame.draw.rect(surface, color, (x, y, w, h), border_radius=10)
    text_surf = FONT.render(text, True, BLUE)
    text_rect = text_surf.get_rect(center=(x + w // 2, y + h // 2))
    surface.blit(text_surf, text_rect)
    return is_hovered

def get_player_name():
    input_name = ""
    while True:
        win.fill(WHITE)
        draw_centered_text("Enter your name:", FONT, BLUE, win, WIDTH//2, HEIGHT//2 - 60)
        draw_centered_text(input_name, FONT, BLUE, win, WIDTH//2, HEIGHT//2)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and input_name.strip():
                    return input_name.strip()
                elif event.key == pygame.K_BACKSPACE:
                    input_name = input_name[:-1]
                else:
                    input_name += event.unicode

def select_difficulty():
    while True:
        win.fill(WHITE)
        mouse_pos = pygame.mouse.get_pos()

        draw_centered_text("Select Difficulty", TITLE_FONT, BLUE, win, WIDTH//2, 100)
        easy_btn = draw_button("Easy", WIDTH//2 - 100, 220, 200, 60, win, mouse_pos)
        medium_btn = draw_button("Medium", WIDTH//2 - 100, 300, 200, 60, win, mouse_pos)
        hard_btn = draw_button("Hard", WIDTH//2 - 100, 380, 200, 60, win, mouse_pos)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if easy_btn:
                    return 5.5, 45, "Easy"
                elif medium_btn:
                    return 3.5, 30, "Medium"
                elif hard_btn:
                    return 2.5, 30, "Hard"

def update_leaderboard(name, score, difficulty="N/A", level=1, lines_cleared=0):
    global leaderboard
    entry = {
        "name": name,
        "score": score,
        "difficulty": difficulty,
        "level": level,
        "lines_cleared": lines_cleared,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    leaderboard.append(entry)
    leaderboard.sort(key=lambda x: x["score"], reverse=True)
    leaderboard = leaderboard[:5]
    save_leaderboard(leaderboard)

def start_menu():
    while True:
        win.fill(WHITE)
        mouse_pos = pygame.mouse.get_pos()

        draw_centered_text("TYPING GAME", TITLE_FONT, BLUE, win, WIDTH//2, 100)
        start_btn = draw_button("Start Game", WIDTH//2 - 100, 250, 200, 60, win, mouse_pos)
        exit_btn = draw_button("Exit", WIDTH//2 - 100, 350, 200, 60, win, mouse_pos)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_btn:
                    return
                if exit_btn:
                    pygame.quit()
                    sys.exit()

def game_loop():
    player_name = get_player_name()
    word_time, TOTAL_GAME_TIME, difficulty = select_difficulty()
    input_text = ""
    current_word = random.choice(words)
    correct = 0
    incorrect = 0
    start_time = time.time()
    word_start_time = start_time
    clock = pygame.time.Clock()

    while True:
        clock.tick(60)
        current_time = time.time()
        elapsed_time = current_time - start_time
        word_elapsed_time = current_time - word_start_time

        if elapsed_time >= TOTAL_GAME_TIME:
            break

        win.fill(WHITE)
        draw_centered_text("Type this word:", FONT, BLUE, win, WIDTH//2, HEIGHT//2 - 100)
        draw_centered_text(current_word, BIG_FONT, BLUE, win, WIDTH//2, HEIGHT//2)
        draw_centered_text("Your Input: " + input_text, FONT, BLUE, win, WIDTH//2, HEIGHT//2 + 120)
        draw_text(f"Correct: {correct}  Incorrect: {incorrect}", FONT, BLUE, win, 100, 50)
        draw_text(f"Time Left: {int(TOTAL_GAME_TIME - elapsed_time)}s", FONT, BLUE, win, 100, 100)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    input_text += event.unicode

        if word_elapsed_time >= word_time:
            if input_text.strip() == current_word:
                correct += 1
            else:
                incorrect += 1
            current_word = random.choice(words)
            input_text = ""
            word_start_time = time.time()

    update_leaderboard(player_name, correct, difficulty)
    show_game_over(correct, incorrect)

def show_game_over(correct, incorrect):
    win.fill(WHITE)
    draw_centered_text("Time's Up!", TITLE_FONT, BLUE, win, WIDTH//2, 100)
    draw_centered_text(f"Correct: {correct}", FONT, BLUE, win, WIDTH//2, 200)
    draw_centered_text(f"Incorrect: {incorrect}", FONT, BLUE, win, WIDTH//2, 250)
    draw_centered_text("Leaderboard:", FONT, BLUE, win, WIDTH//2, 320)

    for i, entry in enumerate(leaderboard):
        draw_centered_text(f"{i+1}. {entry['name']} - {entry['score']}", FONT, BLUE, win, WIDTH//2, 360 + i * 40)

    draw_centered_text("Press R to Restart or Q to Quit", FONT, BLUE, win, WIDTH//2, HEIGHT - 100)
    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    start_menu()
                    game_loop()
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

start_menu()
game_loop()
