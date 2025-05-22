import pygame
import sys
import random
import time
import json
import os
from datetime import datetime

# Initialize Pygame
pygame.init()

# Screen size
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Spell Quest")

# Colors
WHITE = (236, 240, 241)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
BLUE = (52, 152, 219)
TIMER_COLOR = (0, 255, 0)
TIMER_EMPTY_COLOR = (255, 0, 0)

# Fonts
font = pygame.font.SysFont(['San Francisco', 'Helvetica Neue', 'Arial', 'sans-serif'], 32)
big_font = pygame.font.SysFont(['San Francisco', 'Helvetica Neue', 'Arial', 'sans-serif'], 60, bold=True)
clock = pygame.time.Clock()

# Question list
questions = [
  {"word": "banana", "clue": "It is yellow. Monkeys eat it.", "category": "Fruits"},
  {"word": "carrot", "clue": "It is orange. Rabbits eat it.", "category": "Vegetables"},
  {"word": "broccoli", "clue": "It is green. Looks like a tiny tree.", "category": "Vegetables"},
  {"word": "giraffe", "clue": "A very tall animal with a long neck.", "category": "Animals"},
  {"word": "tokyo", "clue": "A big city in Japan.", "category": "Places"},
  {"word": "amazon", "clue": "A very big forest.", "category": "Places"},
  {"word": "mango", "clue": "A sweet yellow fruit.", "category": "Fruits"},
  {"word": "kangaroo", "clue": "It hops. It has a pouch.", "category": "Animals"},
  {"word": "nile", "clue": "A very long river in Africa.", "category": "Places"},
  {"word": "onion", "clue": "A round vegetable. It can make you cry.", "category": "Vegetables"},
  {"word": "zebra", "clue": "Black and white stripes. Looks like a horse.", "category": "Animals"},
  {"word": "sydney", "clue": "A city in Australia. Has a big Opera House.", "category": "Places"}
]


LEADERBOARD_FILE = "leaderboard.json"

def load_leaderboard():
    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, 'r') as f:
            return json.load(f)
    return []

def save_leaderboard(data):
    with open(LEADERBOARD_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def draw_text(text, x, y, color=BLUE, center=False, font_obj=font):
    text_surface = font_obj.render(text, True, color)
    if center:
        text_rect = text_surface.get_rect(center=(x, y))
        screen.blit(text_surface, text_rect)
    else:
        screen.blit(text_surface, (x, y))

def draw_timer_bar(time_left, max_time, x, y, width, height):
    progress_width = (time_left / max_time) * width
    color = TIMER_COLOR if progress_width >= width // 3 else TIMER_EMPTY_COLOR
    pygame.draw.rect(screen, color, pygame.Rect(x, y, progress_width, height))

def animate_flash(text, color, duration=1000):
    start_time = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start_time < duration:
        screen.fill(WHITE)
        draw_text(text, WIDTH // 2, HEIGHT // 2, color=color, center=True, font_obj=big_font)
        pygame.display.flip()
        clock.tick(60)

def animate_shake(text, color, shakes=10, intensity=5):
    for _ in range(shakes):
        offset_x = random.randint(-intensity, intensity)
        offset_y = random.randint(-intensity, intensity)
        screen.fill(WHITE)
        draw_text(text, WIDTH // 2 + offset_x, HEIGHT // 2 + offset_y, color=color, center=True, font_obj=big_font)
        pygame.display.flip()
        pygame.time.delay(50)

def enter_name():
    name = ""
    while True:
        screen.fill(WHITE)
        draw_text("Enter your name:", WIDTH // 2, HEIGHT // 3, center=True)
        draw_text(name, WIDTH // 2, HEIGHT // 2, center=True)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name.strip():
                    return name.strip()
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif len(name) < 15 and event.unicode.isalnum():
                    name += event.unicode

def select_difficulty():
    levels = {
        "1": ("easy", 20),
        "2": ("medium", 15),
        "3": ("master", 10)
    }
    while True:
        screen.fill(WHITE)
        draw_text("Select Difficulty Level", WIDTH // 2, HEIGHT // 3, center=True)
        draw_text("1. Easy", WIDTH // 2, HEIGHT // 2 - 40, center=True)
        draw_text("2. Medium", WIDTH // 2, HEIGHT // 2, center=True)
        draw_text("3. Hard", WIDTH // 2, HEIGHT // 2 + 40, center=True)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.unicode in levels:
                    return levels[event.unicode]

def display_leaderboard():
    leaderboard = load_leaderboard()
    leaderboard = sorted(leaderboard, key=lambda x: x['score'], reverse=True)[:5]

    screen.fill(WHITE)
    draw_text("Leaderboard - Top 5", WIDTH // 2, 50, center=True, font_obj=big_font)
    for idx, entry in enumerate(leaderboard):
        draw_text(f"{idx + 1}. {entry['name']} - {entry['score']}", WIDTH // 2, 150 + idx * 40, center=True)
    draw_text("Press any key to return to main menu", WIDTH // 2, HEIGHT - 60, center=True)
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                waiting = False

def main_menu():
    while True:
        screen.fill(WHITE)
        draw_text("Spell Quest", WIDTH // 2, HEIGHT // 3, center=True, font_obj=big_font)
        draw_text("Press ENTER to Start", WIDTH // 2, HEIGHT // 2, center=True)
        draw_text("Press L for Leaderboard", WIDTH // 2, HEIGHT // 2 + 50, center=True)
        draw_text("Press ESC to Exit", WIDTH // 2, HEIGHT // 2 + 100, center=True)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                if event.key == pygame.K_l:
                    display_leaderboard()

def end_screen(score, name, difficulty):
    leaderboard = load_leaderboard()
    leaderboard.append({
        "name": name,
        "score": score,
        "difficulty": difficulty,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    })
    save_leaderboard(leaderboard)

    while True:
        screen.fill(WHITE)
        draw_text(f"Quiz Over! Your Score: {score}", WIDTH // 2, HEIGHT // 3, center=True)

        if score == len(questions):
            draw_text("Excellent! Perfect Score!", WIDTH // 2, HEIGHT // 3 + 60, center=True)
        elif score >= len(questions) * 0.6:
            draw_text("Good Job!", WIDTH // 2, HEIGHT // 3 + 60, center=True)
        else:
            draw_text("Keep Practicing!", WIDTH // 2, HEIGHT // 3 + 60, center=True)

        draw_text("Press R to Retry, L for Leaderboard, or Q for Quit", WIDTH // 2, HEIGHT // 2 + 80, center=True)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    quiz_game()
                elif event.key == pygame.K_l:
                    display_leaderboard()
                elif event.key == pygame.K_q:
                    return

def quiz_game():
    name = enter_name()
    difficulty_name, time_limit = select_difficulty()
    random.shuffle(questions)
    current = 0
    score = 0

    while current < len(questions):
        input_text = ''
        attempts = 0
        hint_used = False
        paused = False
        answered = False

        question = questions[current]
        clue = question['clue']
        answer = question['word']
        category = question['category']
        start_time = time.time()

        while not answered:
            if not paused:
                screen.fill(WHITE)
                elapsed = int(time.time() - start_time)
                remaining = max(0, time_limit - elapsed)

                draw_text(f"Category: {category}", WIDTH // 2, 40, center=True)
                draw_text(f"Hint: {clue}", WIDTH // 2, 100, center=True)
                draw_text("Your Answer:", 50, 180)
                draw_text(input_text, 250, 180)
                draw_text(f"Score: {score}", WIDTH - 150, 40)

                if hint_used:
                    draw_text(f"Hint: {answer[0]}...", 50, 140)

                draw_text(f"Time Left: {remaining}s", WIDTH // 2, HEIGHT - 70, center=True)
                draw_timer_bar(remaining, time_limit, 0, HEIGHT - 30, WIDTH, 20)

                pygame.display.flip()
                clock.tick(30)

                if remaining == 0:
                    animate_shake(f"Time's up! Answer: {answer}", RED)
                    answered = True
                    break

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if paused and not (event.key == pygame.K_p and not event.mod & pygame.KMOD_SHIFT):
                        continue
                    if event.key == pygame.K_p and not event.mod & pygame.KMOD_SHIFT:
                        paused = not paused
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    elif event.key == pygame.K_RETURN:
                        if input_text.strip() == '':
                            animate_flash("Input can't be empty!", RED)
                        elif input_text.lower() == answer.lower():
                            score += 1
                            animate_flash("Correct!", GREEN, duration=500)
                            answered = True
                        else:
                            attempts += 1
                            if attempts >= 2:
                                animate_shake(f"Wrong! Answer: {answer}", RED)
                                answered = True
                            else:
                                animate_flash("Try Again!", (255, 165, 0), duration=1000)
                    elif event.key == pygame.K_h and not hint_used:
                        hint_used = True
                    elif event.key == pygame.K_ESCAPE:
                        end_screen(score, name, difficulty_name)
                        return
                    else:
                        if len(input_text) < 20 and event.unicode.isalpha():
                            input_text += event.unicode

        current += 1

    end_screen(score, name, difficulty_name)

if __name__ == "__main__":
    main_menu()
    quiz_game()
