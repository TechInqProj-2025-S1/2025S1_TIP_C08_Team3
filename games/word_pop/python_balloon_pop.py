import pygame
import random
import os

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 700
GRID_SIZE = 26
GRID_WIDTH = 10
GRID_HEIGHT = 20
SIDEBAR_WIDTH = 240

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
PURPLE = (155, 89, 182)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
SUCCESS_COLOR = (46, 204, 113)
PRIMARY_COLOR = (52, 152, 219)
SECONDARY_COLOR = (41, 128, 185)
ACCENT_COLOR = (46, 204, 113)
ERROR_COLOR = (231, 76, 60)
BG_COLOR = (236, 240, 241)
TEXT_COLOR = (44, 62, 80)
BALLOON_COLORS = [(241, 196, 15), (231, 76, 60), (52, 152, 219), (155, 89, 182)]
BLOCK_COLORS = [PRIMARY_COLOR, SECONDARY_COLOR, ACCENT_COLOR, (241, 196, 15), PURPLE, ORANGE]

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Balloon Pop - Words")
clock = pygame.time.Clock()

TITLE_FONT = pygame.font.SysFont('Arial', 56, bold=True)
BODY_FONT = pygame.font.SysFont('Arial', 32)
SCORE_FONT = pygame.font.SysFont('Arial', 28, bold=True)
BUTTON_FONT = pygame.font.SysFont('Arial', 24, bold=True)
INPUT_FONT = pygame.font.SysFont('Arial', 28)

score = 0
balloons = []
spawn_timer = 0
spawn_interval = 1500
game_over = False
game_started = False
player_name = ""
input_active = True
max_name_length = 12
difficulty = None
highscore_name = None
highscore_score = 0

HIGHSCORE_FILE = "highscore.txt"

def load_highscore():
    if os.path.exists(HIGHSCORE_FILE):
        with open(HIGHSCORE_FILE, "r") as f:
            line = f.readline().strip()
            if line:
                parts = line.split(",")
                if len(parts) == 2:
                    return parts[0], int(parts[1])
    return None, 0

def save_highscore(name, score):
    with open(HIGHSCORE_FILE, "w") as f:
        f.write(f"{name},{score}")

highscore_name, highscore_score = load_highscore()

class Button:
    def __init__(self, rect, text, bg_color, text_color=WHITE):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.bg_color = bg_color
        self.text_color = text_color
        self.highlight = False

    def draw(self, surface):
        color = tuple(min(255, c+40) if self.highlight else c for c in self.bg_color)
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        text_surf = BUTTON_FONT.render(self.text, True, self.text_color)
        surface.blit(text_surf, text_surf.get_rect(center=self.rect.center))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

    def update_highlight(self, mouse_pos):
        self.highlight = self.rect.collidepoint(mouse_pos)

def load_word_pairs(filename="words.txt"):
    pairs = []
    try:
        with open(filename) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split(",")
                if len(parts) == 2:
                    correct = parts[0].strip()
                    wrong = parts[1].strip()
                    pairs.append((correct, wrong))
    except FileNotFoundError:
        print(f"Error: {filename} not found.")
    return pairs

word_pairs = load_word_pairs()

class Balloon:
    def __init__(self, x, y, word, is_correct, speed):
        self.rect = pygame.Rect(x, y, 120, 80)
        self.word = word
        self.is_correct = is_correct
        self.speed = speed
        self.popped = False
        self.color = random.choice(BALLOON_COLORS)
        self.pop_timer = 0

    def move(self, dt):
        if not self.popped:
            self.rect.y -= self.speed * dt / 1000
        else:
            self.pop_timer += dt
            self.rect.y -= 300 * dt / 1000

    def draw(self, surface):
        if self.popped and self.pop_timer > 500:
            return
        pygame.draw.rect(surface, self.color, self.rect, border_radius=30)
        word_surf = BODY_FONT.render(self.word, True, WHITE)
        surface.blit(word_surf, word_surf.get_rect(center=self.rect.center))

    def pop(self, correct_hit):
        self.popped = True
        self.color = SUCCESS_COLOR if correct_hit else ERROR_COLOR

def reset_game():
    global score, balloons, spawn_timer, game_over
    score = 0
    balloons.clear()
    spawn_timer = 0
    game_over = False

quit_button = Button((SCREEN_WIDTH - 110, 20, 100, 40), "Quit", (231, 76, 60))
restart_button = Button((SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 + 50, 100, 40), "Restart", (46, 204, 113))
gameover_quit_button = Button((SCREEN_WIDTH // 2 + 10, SCREEN_HEIGHT // 2 + 50, 100, 40), "Quit", (231, 76, 60))
highscore_button = Button((SCREEN_WIDTH - 120, 70, 110, 40), "High Score", (52, 152, 219))

difficulty_buttons = [
    Button((SCREEN_WIDTH//2 - 160, 320, 100, 50), "Easy", (46, 204, 113)),
    Button((SCREEN_WIDTH//2 - 50, 320, 100, 50), "Medium", (241, 196, 15)),
    Button((SCREEN_WIDTH//2 + 60, 320, 100, 50), "Hard", (231, 76, 60)),
]

showing_highscore = False

def set_difficulty_params(diff):
    global spawn_interval, balloon_speed
    if diff == "Easy":
        spawn_interval = 2000
        balloon_speed = 100
    elif diff == "Medium":
        spawn_interval = 1300
        balloon_speed = 150
    else:
        spawn_interval = 900
        balloon_speed = 200

running = True
balloon_speed = 120

while running:
    dt = clock.tick(60)
    screen.fill(WHITE)
    mouse_pos = pygame.mouse.get_pos()

    quit_button.update_highlight(mouse_pos)
    restart_button.update_highlight(mouse_pos)
    gameover_quit_button.update_highlight(mouse_pos)
    highscore_button.update_highlight(mouse_pos)
    for btn in difficulty_buttons:
        btn.update_highlight(mouse_pos)

    if not game_started:
        title_text = TITLE_FONT.render("Balloon Pop - Words", True, TEXT_COLOR)
        screen.blit(title_text, title_text.get_rect(center=(SCREEN_WIDTH // 2, 100)))

        instr_text = BODY_FONT.render("Enter your name and press ENTER:", True, TEXT_COLOR)
        screen.blit(instr_text, instr_text.get_rect(center=(SCREEN_WIDTH // 2, 180)))

        input_box = pygame.Rect(SCREEN_WIDTH//2 - 150, 220, 300, 50)
        pygame.draw.rect(screen, (200, 200, 200), input_box, border_radius=5)
        name_surf = INPUT_FONT.render(player_name, True, TEXT_COLOR)
        screen.blit(name_surf, (input_box.x + 10, input_box.y + 10))

        diff_text = BODY_FONT.render("Select Difficulty:", True, TEXT_COLOR)
        screen.blit(diff_text, diff_text.get_rect(center=(SCREEN_WIDTH // 2, 290)))

        for btn in difficulty_buttons:
            btn.draw(screen)

        highscore_button.draw(screen)

        if showing_highscore:
            pygame.draw.rect(screen, (220, 220, 220), (SCREEN_WIDTH//2 - 160, 400, 330, 120), border_radius=10)
            hs_title = BODY_FONT.render("High Score", True, TEXT_COLOR)
            screen.blit(hs_title, hs_title.get_rect(center=(SCREEN_WIDTH // 2, 430)))
            if highscore_name:
                hs_text = BODY_FONT.render(f"{highscore_name} - {highscore_score}", True, TEXT_COLOR)
                screen.blit(hs_text, hs_text.get_rect(center=(SCREEN_WIDTH // 2, 470)))
            else:
                no_hs = BODY_FONT.render("No high score yet", True, TEXT_COLOR)
                screen.blit(no_hs, no_hs.get_rect(center=(SCREEN_WIDTH // 2, 470)))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                elif event.key == pygame.K_RETURN:
                    if len(player_name) > 0 and difficulty:
                        game_started = True
                        set_difficulty_params(difficulty)
                else:
                    if len(player_name) < max_name_length and event.unicode.isprintable():
                        player_name += event.unicode
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    input_active = True
                else:
                    input_active = False
                for btn in difficulty_buttons:
                    if btn.is_clicked(event.pos):
                        difficulty = btn.text
                if highscore_button.is_clicked(event.pos):
                    showing_highscore = not showing_highscore
                if quit_button.is_clicked(event.pos):
                    running = False

        quit_button.draw(screen)

    else:
        if not game_over:
            spawn_timer += dt
            if spawn_timer > spawn_interval:
                spawn_timer = 0
                pair = random.choice(word_pairs)
                is_correct = random.choice([True, False])
                word = pair[0] if is_correct else pair[1]
                x = random.randint(50, SCREEN_WIDTH - 170)
                y = SCREEN_HEIGHT + 80
                balloons.append(Balloon(x, y, word, is_correct, balloon_speed))

            for b in balloons[:]:
                b.move(dt)
                if b.rect.bottom < 0 or (b.popped and b.pop_timer > 500):
                    balloons.remove(b)

            for b in balloons:
                b.draw(screen)

            score_surf = SCORE_FONT.render(f"Score: {score}", True, TEXT_COLOR)
            screen.blit(score_surf, (20, 20))

            name_surf = SCORE_FONT.render(f"Player: {player_name}", True, TEXT_COLOR)
            screen.blit(name_surf, (20, 50))

            difficulty_surf = SCORE_FONT.render(f"Difficulty: {difficulty}", True, TEXT_COLOR)
            screen.blit(difficulty_surf, (20, 80))

            quit_button.draw(screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if quit_button.is_clicked(event.pos):
                        running = False
                    else:
                        for b in balloons:
                            if b.rect.collidepoint(event.pos) and not b.popped:
                                if b.is_correct:
                                    b.pop(True)
                                    score += 1
                                else:
                                    b.pop(False)
                                    game_over = True
                                break
        else:
            over_text = TITLE_FONT.render("Game Over", True, ERROR_COLOR)
            screen.blit(over_text, over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)))

            final_score_text = BODY_FONT.render(f"Your Score: {score}", True, TEXT_COLOR)
            screen.blit(final_score_text, final_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)))

            if score > highscore_score:
                congrats_text = BODY_FONT.render("New High Score!", True, SUCCESS_COLOR)
                screen.blit(congrats_text, congrats_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40)))
                save_highscore(player_name, score)
                highscore_name = player_name
                highscore_score = score

            restart_button.draw(screen)
            gameover_quit_button.draw(screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if restart_button.is_clicked(event.pos):
                        reset_game()
                        game_started = False
                        player_name = ""
                        difficulty = None
                        showing_highscore = False
                    elif gameover_quit_button.is_clicked(event.pos):
                        running = False

    pygame.display.flip()

pygame.quit()
