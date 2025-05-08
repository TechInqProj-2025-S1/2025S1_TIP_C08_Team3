import pygame
import sys
import random
import time

# Initialize Pygame
pygame.init()

# Screen size
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Typing Speed Quiz")

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
BLUE = (0, 0, 255)
TIMER_COLOR = (0, 255, 0)
TIMER_EMPTY_COLOR = (255, 0, 0)

# Fonts
font = pygame.font.SysFont('calibri', 35)
big_font = pygame.font.SysFont('calibri', 66, bold=True)
clock = pygame.time.Clock()

# Question list
questions = [
    {"word": "apple", "clue": "A fruit that keeps the doctor away", "category": "Fruits"},
    {"word": "banana", "clue": "A yellow fruit monkeys love", "category": "Fruits"},
    {"word": "grapes", "clue": "Small and round, used to make wine", "category": "Fruits"},
    {"word": "carrot", "clue": "Orange root vegetable, rabbits love it", "category": "Vegetables"},
    {"word": "broccoli", "clue": "A green vegetable that looks like a tree", "category": "Vegetables"},
    {"word": "penguin", "clue": "A bird that swims and lives in the cold", "category": "Animals"},
    {"word": "giraffe", "clue": "Tallest land animal with a long neck", "category": "Animals"},
    {"word": "tokyo", "clue": "Capital of Japan, known for technology", "category": "Places"},
    {"word": "amazon", "clue": "Largest rainforest in the world", "category": "Places"},
]

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

def main_menu():
    while True:
        screen.fill(WHITE)
        draw_text("Spell Quest", WIDTH // 2, HEIGHT // 3, center=True, font_obj=big_font)
        draw_text("Press ENTER to Start", WIDTH // 2, HEIGHT // 2, center=True)
        draw_text("Press ESC to Exit", WIDTH // 2, HEIGHT // 2 + 50, center=True)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()

def quiz_game():
    random.shuffle(questions)
    current = 0
    score = 0
    time_limit = 15

    while current < len(questions):
        input_text = ''
        attempts = 0
        hint_used = False
        show_result = False
        paused = False
        result_msg = ''
        result_color = BLUE
        start_time = time.time()

        question = questions[current]
        clue = question['clue']
        answer = question['word']
        category = question['category']

        while True:
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

                if show_result:
                    draw_text(result_msg, WIDTH // 2, 250, result_color, center=True)

                draw_text(f"Time Left: {remaining}s", WIDTH // 2, HEIGHT - 70, center=True)
                draw_timer_bar(remaining, time_limit, 0, HEIGHT - 30, WIDTH, 20)

                pygame.display.flip()
                clock.tick(30)

                if remaining == 0:
                    result_msg = f"Time’s up! Answer: {answer}"
                    show_result = True
                    pygame.display.flip()
                    pygame.time.delay(1500)
                    current += 1
                    break

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if paused and event.key != pygame.K_p:
                        continue
                    if event.key == pygame.K_p:
                        paused = not paused
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    elif event.key == pygame.K_RETURN:
                        if input_text.strip() == '':
                            result_msg = "Input can't be empty!"
                            show_result = True
                        elif input_text.lower() == answer.lower():
                            result_msg = "Correct!"
                            score += 1
                            show_result = True
                            pygame.display.flip()
                            pygame.time.delay(1500)
                            current += 1
                            break
                        else:
                            attempts += 1
                            if attempts >= 2:
                                result_msg = f"Wrong! Answer: {answer}"
                                show_result = True
                                pygame.display.flip()
                                pygame.time.delay(1500)
                                current += 1
                                break
                            else:
                                result_msg = "Try again!"
                                show_result = True
                    elif event.key == pygame.K_h and not hint_used:
                        hint_used = True
                    elif event.key == pygame.K_ESCAPE:
                        return
                    else:
                        if len(input_text) < 20 and event.unicode.isalpha():
                            input_text += event.unicode

    end_screen(score)

def end_screen(score):
    while True:
        screen.fill(WHITE)
        draw_text(f"Quiz Over! Your Score: {score}", WIDTH // 2, HEIGHT // 3, center=True)

        if score == len(questions):
            draw_text("🎉 Excellent! Perfect Score!", WIDTH // 2, HEIGHT // 3 + 60, center=True)
        elif score >= len(questions) * 0.6:
            draw_text("👍 Good Job!", WIDTH // 2, HEIGHT // 3 + 60, center=True)
        else:
            draw_text("📚 Keep Practicing!", WIDTH // 2, HEIGHT // 3 + 60, center=True)

        draw_text("Press R to Retry or ESC to Exit", WIDTH // 2, HEIGHT // 2 + 80, center=True)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    quiz_game()
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()

if __name__ == "__main__":
    main_menu()
    quiz_game()
