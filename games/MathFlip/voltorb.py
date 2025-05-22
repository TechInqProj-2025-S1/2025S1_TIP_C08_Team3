import pygame
import sys
import random
import os
import json
from pygame.locals import *

# Score file path for launcher compatibility
SCORE_FILE = os.path.join('scores', 'math_flip_scores.json')

# Initialize pygame
pygame.init()


# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60
GRID_SIZE = 5
# CELL_SIZE, GRID_OFFSET_X, GRID_OFFSET_Y will be computed dynamically
ANSWER_CELL_HEIGHT = 60  # Height for answer cells (width is dynamic)



# THEME COLORS (match launcher)
BG_COLOR = (236, 240, 241)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)  # For grid background/unrevealed
PRIMARY_COLOR = (52, 152, 219)  # Blue
SECONDARY_COLOR = (41, 128, 185)  # Darker Blue
ACCENT_COLOR = (46, 204, 113)  # Green
WARNING_COLOR = (231, 76, 60)  # Red
SECONDARY_WARNING_COLOR = (192, 57, 43)  # Darker Red
TEXT_COLOR = (44, 62, 80)  # Dark Gray
BUTTON_COLOR = (102, 187, 239)
BUTTON_HOVER_COLOR = (82, 167, 219)
BUTTON_TEXT_COLOR = (255, 255, 255)
LIGHT_GREEN = ACCENT_COLOR
LIGHT_BLUE = PRIMARY_COLOR
LIGHT_RED = WARNING_COLOR
YELLOW = (255, 255, 0)
BLUE = PRIMARY_COLOR

# Game difficulty levels
EASY = "Easy"
NORMAL = "Normal"
HARD = "Hard"


# Set up the game window (will be initialized in MathFlipGame)
DISPLAYSURF = None
CLOCK = None

# Fonts (match launcher/Tetris Math style)
def get_launcher_fonts():
    # Use prioritized list for cross-platform consistency
    font_list = ['San Francisco', 'Helvetica Neue', 'Arial', 'sans-serif']
    if not pygame.font.get_init():
        pygame.font.init()
    return {
        'TITLE_FONT': pygame.font.SysFont(font_list, 60, bold=True),
        'BODY_FONT': pygame.font.SysFont(font_list, 32),
        'SCORE_FONT': pygame.font.SysFont(font_list, 28),
    }

_FONTS = get_launcher_fonts()
FONT_LARGE = _FONTS['TITLE_FONT']
FONT_MEDIUM = _FONTS['BODY_FONT']
FONT_SMALL = _FONTS['SCORE_FONT']

# Function to check if highscore file exists, if not create it
def initialize_highscores():
    if not os.path.exists(SCORE_FILE):
        empty_scores = {
            "Easy": [],
            "Normal": [],
            "Hard": []
        }
        os.makedirs(os.path.dirname(SCORE_FILE), exist_ok=True)
        with open(SCORE_FILE, 'w', encoding='utf-8') as f:
            json.dump(empty_scores, f)

# Function to load high scores
def load_highscores():
    try:
        with open(SCORE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        initialize_highscores()
        return load_highscores()

# Function to save high scores
def save_highscores(highscores):
    with open(SCORE_FILE, 'w', encoding='utf-8') as f:
        json.dump(highscores, f)

# Function to update high scores
def update_highscores(difficulty, player_name, score):
    highscores = load_highscores()
    
    # Add new score
    highscores[difficulty].append({"name": player_name, "score": score})
    
    # Sort by score and keep only top 5
    highscores[difficulty] = sorted(highscores[difficulty], key=lambda x: x["score"], reverse=True)[:5]
    
    # Save back to file
    save_highscores(highscores)

# Game class
class MathFlipGame:
    def __init__(self, screen_width=None, screen_height=None, fullscreen=True, screen=None):
        import os
        import json
        global DISPLAYSURF, CLOCK, WINDOW_WIDTH, WINDOW_HEIGHT
        # Try to read launcher config for display settings
        info = pygame.display.Info()
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config.json")
        launcher_display = None
        if os.path.exists(config_path):
            try:
                with open(config_path, "r") as f:
                    config = json.load(f)
                launcher_display = config.get("launcher", {}).get("display", None)
            except Exception:
                launcher_display = None
        if launcher_display:
            screen_width = launcher_display.get("width", info.current_w)
            screen_height = launcher_display.get("height", info.current_h)
        if screen_width is None:
            screen_width = info.current_w
        if screen_height is None:
            screen_height = info.current_h
        WINDOW_WIDTH = screen_width
        WINDOW_HEIGHT = screen_height
        if screen is not None:
            DISPLAYSURF = screen
        else:
            # Always use fullscreen borderless (NOFRAME)
            flags = pygame.NOFRAME
            DISPLAYSURF = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), flags)
            pygame.display.set_caption('Math Flip Game')
        CLOCK = pygame.time.Clock()
        # --- Dynamic grid scaling ---
        self.GRID_SIZE = GRID_SIZE
        # The grid should fit within 60% of the window height and 60% of the window width (leaving room for UI)
        max_grid_width = int(WINDOW_WIDTH * 0.6)
        max_grid_height = int(WINDOW_HEIGHT * 0.6)
        self.CELL_SIZE = min(max_grid_width // self.GRID_SIZE, max_grid_height // self.GRID_SIZE)
        self.GRID_PIXEL_SIZE = self.CELL_SIZE * self.GRID_SIZE
        # Center the grid horizontally and vertically (with some top margin for title/timer)
        self.GRID_OFFSET_X = (WINDOW_WIDTH - self.GRID_PIXEL_SIZE) // 2
        self.GRID_OFFSET_Y = max(70, (WINDOW_HEIGHT - self.GRID_PIXEL_SIZE) // 2 - 40)
        # ---
        self.state = "menu"  # menu, difficulty, game, game_over
        self.difficulty = EASY
        self.score = 0
        self.grid = []
        self.revealed = []
        self.correct_matches = 0
        self.total_matches = 0
        self.selected_cell = None
        self.dragging = False
        self.answers = []
        self.selected_answer = None
        self.initialize_highscores()
        self.player_name = ""
        self.name_input_active = False
        self.timer = 60  # 60 seconds timer for the game
        self.last_time = pygame.time.get_ticks()
    
    def initialize_highscores(self):
        initialize_highscores()
    
    def reset_game(self):
        self.grid = []
        self.revealed = [[False for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.answers = []
        self.score = 0
        self.correct_matches = 0
        self.selected_cell = None
        self.selected_answer = None
        self.dragging = False
        self.timer = 60  # Reset timer
        self.last_time = pygame.time.get_ticks()
        
        # Generate questions and answers based on difficulty
        self.generate_questions()
        self.total_matches = len([cell for row in self.grid for cell in row if cell is not None])
    
    def generate_questions(self):
        operations = []
        
        if self.difficulty == EASY:
            operations = ["+"]
        elif self.difficulty == NORMAL:
            operations = ["+", "-"]
        elif self.difficulty == HARD:
            operations = ["+", "-", "*", "/"]
        
        # Generate grid of questions
        self.grid = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        
        # Select random cells to put questions in (not all cells will have questions)
        num_questions = random.randint(15, 20)  # Between 15-20 questions
        possible_positions = [(i, j) for i in range(GRID_SIZE) for j in range(GRID_SIZE)]
        question_positions = random.sample(possible_positions, num_questions)
        
        # Generate questions for selected positions
        unique_answers = set()
        for pos in question_positions:
            i, j = pos
            question, answer = self.generate_single_question(operations)
            self.grid[i][j] = (question, answer)
            unique_answers.add(answer)
        
        # Convert unique answers to list and select 5 (or less if there are fewer unique answers)
        unique_answers_list = list(unique_answers)
        if len(unique_answers_list) <= 5:
            self.answers = unique_answers_list
        else:
            self.answers = random.sample(unique_answers_list, 5)
        
        # Add "Other" as the last option
        self.answers.append("Other")
    
    def generate_single_question(self, operations):
        operation = random.choice(operations)
        
        if operation == "+":
            a = random.randint(1, 20)
            b = random.randint(1, 20)
            question = f"{a} + {b}"
            answer = a + b
        
        elif operation == "-":
            a = random.randint(1, 20)
            b = random.randint(1, a)  # Ensure a >= b for primary school level
            question = f"{a} - {b}"
            answer = a - b
        
        elif operation == "*":
            a = random.randint(1, 10)
            b = random.randint(1, 10)
            question = f"{a} × {b}"
            answer = a * b
        
        elif operation == "/":
            b = random.randint(1, 10)
            a = b * random.randint(1, 10)  # Ensure division results in whole number
            question = f"{a} ÷ {b}"
            answer = a // b
        
        return question, answer
    
    def draw_menu(self):
        DISPLAYSURF.fill(BG_COLOR)
        # Draw title
        title = FONT_LARGE.render("Math Flip Game", True, PRIMARY_COLOR)
        title_y = 120
        DISPLAYSURF.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, title_y))

        # Button layout
        button_width = 240
        button_height = 56
        spacing = 32
        center_x = WINDOW_WIDTH // 2
        start_y = title_y + title.get_height() + 60

        # Play button
        play_button = pygame.Rect(center_x - button_width//2, start_y, button_width, button_height)
        pygame.draw.rect(DISPLAYSURF, BUTTON_COLOR, play_button, border_radius=16)
        play_text = FONT_MEDIUM.render("Play", True, BUTTON_TEXT_COLOR)
        DISPLAYSURF.blit(play_text, (play_button.centerx - play_text.get_width()//2, play_button.centery - play_text.get_height()//2))

        # Back to Menu button
        back_button = pygame.Rect(center_x - button_width//2, play_button.bottom + spacing, button_width, button_height)
        pygame.draw.rect(DISPLAYSURF, SECONDARY_COLOR, back_button, border_radius=16)
        back_text = FONT_MEDIUM.render("Back to Menu", True, BUTTON_TEXT_COLOR)
        DISPLAYSURF.blit(back_text, (back_button.centerx - back_text.get_width()//2, back_button.centery - back_text.get_height()//2))

        return [play_button, back_button]
    
    def draw_difficulty_selection(self):
        DISPLAYSURF.fill(BG_COLOR)
        # Draw title
        title = FONT_LARGE.render("Select Difficulty", True, PRIMARY_COLOR)
        title_y = 100
        DISPLAYSURF.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, title_y))

        # Layout parameters
        button_width = 180
        button_height = 48
        spacing = 24
        desc_spacing = 8
        desc_to_button_spacing = 24  # More space between desc and next button
        center_x = WINDOW_WIDTH // 2
        start_y = title_y + title.get_height() + 48

        # Center all three buttons horizontally, stack vertically with spacing and enough gap for description
        button_gap = 32
        desc_gap = 10  # vertical gap between button and its description

        # Easy
        easy_button_y = start_y
        easy_button = pygame.Rect(center_x - button_width//2, easy_button_y, button_width, button_height)
        pygame.draw.rect(DISPLAYSURF, ACCENT_COLOR, easy_button, border_radius=12)
        easy_text = FONT_MEDIUM.render("Easy", True, BUTTON_TEXT_COLOR)
        DISPLAYSURF.blit(easy_text, (easy_button.centerx - easy_text.get_width()//2, easy_button.centery - easy_text.get_height()//2))
        easy_desc = FONT_SMALL.render("Addition only", True, TEXT_COLOR)
        easy_desc_y = easy_button.bottom + desc_gap
        DISPLAYSURF.blit(easy_desc, (center_x - easy_desc.get_width()//2, easy_desc_y))

        # Normal
        normal_button_y = easy_desc_y + easy_desc.get_height() + button_gap
        normal_button = pygame.Rect(center_x - button_width//2, normal_button_y, button_width, button_height)
        pygame.draw.rect(DISPLAYSURF, PRIMARY_COLOR, normal_button, border_radius=12)
        normal_text = FONT_MEDIUM.render("Normal", True, BUTTON_TEXT_COLOR)
        DISPLAYSURF.blit(normal_text, (normal_button.centerx - normal_text.get_width()//2, normal_button.centery - normal_text.get_height()//2))
        normal_desc = FONT_SMALL.render("Addition and Subtraction", True, TEXT_COLOR)
        normal_desc_y = normal_button.bottom + desc_gap
        DISPLAYSURF.blit(normal_desc, (center_x - normal_desc.get_width()//2, normal_desc_y))

        # Hard
        hard_button_y = normal_desc_y + normal_desc.get_height() + button_gap
        hard_button = pygame.Rect(center_x - button_width//2, hard_button_y, button_width, button_height)
        pygame.draw.rect(DISPLAYSURF, WARNING_COLOR, hard_button, border_radius=12)
        hard_text = FONT_MEDIUM.render("Hard", True, BUTTON_TEXT_COLOR)
        DISPLAYSURF.blit(hard_text, (hard_button.centerx - hard_text.get_width()//2, hard_button.centery - hard_text.get_height()//2))
        hard_desc = FONT_SMALL.render("Addition, Subtraction, Multiplication, Division", True, TEXT_COLOR)
        hard_desc_y = hard_button.bottom + desc_gap
        DISPLAYSURF.blit(hard_desc, (center_x - hard_desc.get_width()//2, hard_desc_y))

        # Back button (centered below all options)
        # Calculate bottom y after hard_desc
        bottom_y = hard_desc_y + hard_desc.get_height() + 32
        back_button_width = 120
        back_button_height = 44
        back_button_x = center_x - back_button_width // 2
        back_button_y = bottom_y
        back_button = pygame.Rect(back_button_x, back_button_y, back_button_width, back_button_height)
        pygame.draw.rect(DISPLAYSURF, SECONDARY_COLOR, back_button, border_radius=12)
        back_text = FONT_SMALL.render("Back", True, BUTTON_TEXT_COLOR)
        DISPLAYSURF.blit(back_text, (back_button.centerx - back_text.get_width()//2, back_button.centery - back_text.get_height()//2))

        return [easy_button, normal_button, hard_button, back_button]
    

    
    def draw_game(self):
        DISPLAYSURF.fill(BG_COLOR)
        # Title and HUD
        title = FONT_MEDIUM.render(f"Math Flip Game - {self.difficulty}", True, PRIMARY_COLOR)
        DISPLAYSURF.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 20))
        score_text = FONT_MEDIUM.render(f"Score: {self.score}", True, TEXT_COLOR)
        DISPLAYSURF.blit(score_text, (32, 20))
        timer_text = FONT_MEDIUM.render(f"Time: {self.timer}", True, TEXT_COLOR)
        DISPLAYSURF.blit(timer_text, (WINDOW_WIDTH - 170, 20))
        progress_text = FONT_SMALL.render(f"Matched: {self.correct_matches}/{self.total_matches}", True, TEXT_COLOR)
        DISPLAYSURF.blit(progress_text, (WINDOW_WIDTH//2 - progress_text.get_width()//2, 54))

        # --- Draw grid (scaled and centered, rounded, themed) ---
        answer_cells = []
        for i in range(self.GRID_SIZE):
            for j in range(self.GRID_SIZE):
                cell_rect = pygame.Rect(
                    self.GRID_OFFSET_X + j * self.CELL_SIZE,
                    self.GRID_OFFSET_Y + i * self.CELL_SIZE,
                    self.CELL_SIZE,
                    self.CELL_SIZE
                )
                # Determine box color
                if self.revealed[i][j] and (i, j) in getattr(self, 'answered_cells', set()):
                    color = ACCENT_COLOR  # answered
                elif self.revealed[i][j]:
                    color = PRIMARY_COLOR  # revealed but not answered
                else:
                    color = GRAY  # unrevealed
                pygame.draw.rect(DISPLAYSURF, color, cell_rect, border_radius=12)
                pygame.draw.rect(DISPLAYSURF, SECONDARY_COLOR, cell_rect, 2, border_radius=12)
                # Draw question if revealed (not answered) or being dragged
                if self.revealed[i][j] and (i, j) not in getattr(self, 'answered_cells', set()):
                    if self.grid[i][j] is not None:
                        if self.selected_cell == (i, j) and self.dragging:
                            # Draw at mouse position (handled below)
                            pass
                        else:
                            cell_value = self.grid[i][j]
                            if cell_value is not None and cell_value[0] is not None:
                                question_text = FONT_SMALL.render(str(cell_value[0]), True, WHITE)
                                if question_text:
                                    DISPLAYSURF.blit(question_text, (cell_rect.centerx - question_text.get_width()//2, cell_rect.centery - question_text.get_height()//2))

        # If dragging, draw the selected question at mouse position
        if self.dragging and self.selected_cell is not None:
            i, j = self.selected_cell
            cell_value = self.grid[i][j]
            if cell_value is not None and cell_value[0] is not None:
                mouse_pos = pygame.mouse.get_pos()
                # Check if hovering over any answer cell
                hover_on_answer = False
                hover_rect = None
                if self.answers and len(self.answers) > 0:
                    answer_bar_width = min(WINDOW_WIDTH - 40, self.GRID_PIXEL_SIZE)
                    answer_width = answer_bar_width // len(self.answers)
                    answer_bar_x = (WINDOW_WIDTH - answer_bar_width) // 2
                    answer_bar_y = self.GRID_OFFSET_Y + self.GRID_PIXEL_SIZE + 40
                    for idx in range(len(self.answers)):
                        cell_rect = pygame.Rect(
                            answer_bar_x + idx * answer_width,
                            answer_bar_y,
                            answer_width,
                            ANSWER_CELL_HEIGHT
                        )
                        if cell_rect.collidepoint(mouse_pos):
                            hover_on_answer = True
                            hover_rect = cell_rect
                            break
                question_text = FONT_SMALL.render(str(cell_value[0]), True, WHITE)
                if question_text:
                    if hover_on_answer and hover_rect is not None:
                        # Draw the question centered above the answer cell
                        qrect = question_text.get_rect(midbottom=(hover_rect.centerx, hover_rect.top - 8))
                        pygame.draw.rect(DISPLAYSURF, PRIMARY_COLOR, qrect.inflate(20, 10), border_radius=10)
                        pygame.draw.rect(DISPLAYSURF, SECONDARY_COLOR, qrect.inflate(20, 10), 2, border_radius=10)
                        DISPLAYSURF.blit(question_text, qrect)
                    else:
                        question_rect = question_text.get_rect(center=mouse_pos)
                        pygame.draw.rect(DISPLAYSURF, PRIMARY_COLOR, question_rect.inflate(20, 10), border_radius=10)
                        pygame.draw.rect(DISPLAYSURF, SECONDARY_COLOR, question_rect.inflate(20, 10), 2, border_radius=10)
                        DISPLAYSURF.blit(question_text, question_rect)

        # --- Draw answer bar (centered below grid, themed, rounded) ---
        if self.answers and len(self.answers) > 0:
            answer_bar_width = min(WINDOW_WIDTH - 40, self.GRID_PIXEL_SIZE)
            answer_width = answer_bar_width // len(self.answers)
            answer_bar_x = (WINDOW_WIDTH - answer_bar_width) // 2
            answer_bar_y = self.GRID_OFFSET_Y + self.GRID_PIXEL_SIZE + 40
            for i, answer in enumerate(self.answers):
                cell_rect = pygame.Rect(
                    answer_bar_x + i * answer_width,
                    answer_bar_y,
                    answer_width,
                    ANSWER_CELL_HEIGHT
                )
                # Use accent for selected, primary for others
                cell_color = ACCENT_COLOR if self.selected_answer == i else PRIMARY_COLOR
                pygame.draw.rect(DISPLAYSURF, cell_color, cell_rect, border_radius=14)
                pygame.draw.rect(DISPLAYSURF, SECONDARY_COLOR, cell_rect, 2, border_radius=14)
                answer_text = FONT_MEDIUM.render(str(answer), True, WHITE)
                if answer_text:
                    DISPLAYSURF.blit(answer_text, (cell_rect.centerx - answer_text.get_width()//2, cell_rect.centery - answer_text.get_height()//2))
                answer_cells.append(cell_rect)

        # --- Draw back/menu button (bottom left, themed) ---
        back_button = pygame.Rect(32, WINDOW_HEIGHT - 70, 120, 44)
        pygame.draw.rect(DISPLAYSURF, BUTTON_COLOR, back_button, border_radius=12)
        back_text = FONT_SMALL.render("Menu", True, BUTTON_TEXT_COLOR)
        DISPLAYSURF.blit(back_text, (back_button.centerx - back_text.get_width()//2, back_button.centery - back_text.get_height()//2))

        return answer_cells, back_button

    def draw_game_over(self):
        DISPLAYSURF.fill(WHITE)
        # Draw title
        title = FONT_LARGE.render("Game Over!", True, BLUE)
        DISPLAYSURF.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 100))
        # Calculate and display bonus (remaining time)
        if not hasattr(self, '_bonus_added'):
            self._bonus_value = self.timer if self.timer > 0 else 0
            self.score += self._bonus_value
            self._bonus_added = True
        bonus = getattr(self, '_bonus_value', 0)
        if bonus > 0:
            bonus_text = FONT_MEDIUM.render(f"Bonus for time left: +{bonus}", True, (0, 128, 0))
            DISPLAYSURF.blit(bonus_text, (WINDOW_WIDTH//2 - bonus_text.get_width()//2, 160))
            score_y = 200
        else:
            score_y = 200
        # Draw score
        score_text = FONT_LARGE.render(f"Your Score: {self.score}", True, BLACK)
        DISPLAYSURF.blit(score_text, (WINDOW_WIDTH//2 - score_text.get_width()//2, score_y))
        # Draw input for player name if it's a high score
        highscores = load_highscores()
        scores_list = highscores.get(self.difficulty, [])
        is_high_score = (len(scores_list) < 5 or (scores_list and self.score > min(score["score"] for score in scores_list)))
        name_input_rect = None
        submit_button = None
        if is_high_score:
            prompt_text = FONT_MEDIUM.render("New High Score! Enter your name:", True, BLACK)
            DISPLAYSURF.blit(prompt_text, (WINDOW_WIDTH//2 - prompt_text.get_width()//2, 280))
            name_input_rect = pygame.Rect(WINDOW_WIDTH//2 - 150, 330, 300, 40)
            # Always white background for input
            pygame.draw.rect(DISPLAYSURF, WHITE, name_input_rect, border_radius=10)
            pygame.draw.rect(DISPLAYSURF, BLACK, name_input_rect, 2, border_radius=10)
            name_text = FONT_MEDIUM.render(self.player_name, True, BLACK)
            DISPLAYSURF.blit(name_text, (name_input_rect.x + 10, name_input_rect.centery - name_text.get_height()//2))
            # Draw submit button if name is entered
            if len(self.player_name) > 0:
                submit_button = pygame.Rect(WINDOW_WIDTH//2 - 75, 390, 150, 44)
                # Match Tetris Math button style: blue, border radius 10, white text
                pygame.draw.rect(DISPLAYSURF, PRIMARY_COLOR, submit_button, border_radius=10)
                pygame.draw.rect(DISPLAYSURF, ACCENT_COLOR, submit_button, 2, border_radius=10)
                submit_text = FONT_MEDIUM.render("Submit", True, WHITE)
                DISPLAYSURF.blit(submit_text, (submit_button.centerx - submit_text.get_width()//2, submit_button.centery - submit_text.get_height()//2))
        return None, name_input_rect, submit_button
    
    def handle_menu_click(self, mouse_pos, buttons):
        for i, button in enumerate(buttons):
            if button.collidepoint(mouse_pos):
                if i == 0:  # Play button
                    self.state = "difficulty"
                elif i == 1:  # Back to Menu button
                    self.state = "exit_to_launcher"
    
    def handle_difficulty_click(self, mouse_pos, buttons):
        for i, button in enumerate(buttons):
            if button.collidepoint(mouse_pos):
                if i == 0:  # Easy button
                    self.difficulty = EASY
                    self.reset_game()
                    self.state = "game"
                elif i == 1:  # Normal button
                    self.difficulty = NORMAL
                    self.reset_game()
                    self.state = "game"
                elif i == 2:  # Hard button
                    self.difficulty = HARD
                    self.reset_game()
                    self.state = "game"
                elif i == 3:  # Back button
                    self.state = "menu"
    

    
    def handle_game_click(self, mouse_pos, answer_cells, back_button):
        # Check if back button was clicked
        if back_button and back_button.collidepoint(mouse_pos):
            self.state = "menu"
            return
        # Check if answer cell was clicked (handled on drop)
        # Check if grid cell was clicked
        if not answer_cells:
            answer_cells = []
        for i in range(self.GRID_SIZE):
            for j in range(self.GRID_SIZE):
                cell_rect = pygame.Rect(
                    self.GRID_OFFSET_X + j * self.CELL_SIZE,
                    self.GRID_OFFSET_Y + i * self.CELL_SIZE,
                    self.CELL_SIZE,
                    self.CELL_SIZE
                )
                if cell_rect.collidepoint(mouse_pos):
                    # If not revealed, reveal it (and only one at a time)
                    if not self.revealed[i][j]:
                        # Unreveal all non-answered cells
                        for x in range(self.GRID_SIZE):
                            for y in range(self.GRID_SIZE):
                                if self.revealed[x][y] and (x, y) not in getattr(self, 'answered_cells', set()):
                                    self.revealed[x][y] = False
                        self.revealed[i][j] = True
                        self.selected_cell = (i, j)
                        self.dragging = False
                        return
                    # If revealed and not answered, start dragging
                    elif (i, j) not in getattr(self, 'answered_cells', set()) and self.revealed[i][j]:
                        self.selected_cell = (i, j)
                        self.dragging = True
                        return

    def handle_mouse_up(self, mouse_pos, answer_cells):
        if self.dragging and self.selected_cell is not None:
            i, j = self.selected_cell
            cell_value = self.grid[i][j]
            if cell_value is not None:
                question, correct_answer = cell_value
                if not answer_cells:
                    answer_cells = []
                for answer_idx, cell in enumerate(answer_cells):
                    if cell.collidepoint(mouse_pos):
                        if self.answers and answer_idx < len(self.answers):
                            selected_answer = self.answers[answer_idx]
                        else:
                            selected_answer = None
                        if not hasattr(self, 'answered_cells'):
                            self.answered_cells = set()
                        # Check if answer is correct
                        if (selected_answer == "Other" and correct_answer not in self.answers[:-1]) or (selected_answer == correct_answer):
                            self.score += 10
                            self.correct_matches += 1
                            self.answered_cells.add((i, j))
                            # Give bonus time for correct matches
                            self.timer += 5
                        else:
                            self.score = max(0, self.score - 5)
                            self.timer = max(1, self.timer - 3)
                        break
            self.dragging = False
            # If not dropped on answer, keep revealed and available for dragging
            # If dropped on answer, mark as answered (handled above)
            self.selected_cell = None
            # Check if all questions are matched
            if hasattr(self, 'answered_cells') and self.correct_matches >= self.total_matches:
                self.score += self.timer * 2
                self.state = "game_over"
    
    def handle_key_down(self, key):
        if self.state == "game_over" and self.name_input_active:
            if key == K_BACKSPACE:
                self.player_name = self.player_name[:-1]
            elif key == K_RETURN and len(self.player_name) > 0:
                # Add remaining time as bonus before saving high score
                highscores = load_highscores()
                scores_list = highscores.get(self.difficulty, [])
                is_high_score = (len(scores_list) < 5 or (scores_list and self.score > min(score["score"] for score in scores_list)))
                if is_high_score:
                    self.score += self.timer
                    update_highscores(self.difficulty, self.player_name, self.score)
                self.state = "menu"
                self.name_input_active = False
                self.player_name = ""
            elif len(self.player_name) < 10 and (key in range(K_a, K_z + 1) or key in range(K_0, K_9 + 1) or key == K_SPACE):
                self.player_name += chr(key).upper()
    
    def update_timer(self):
        if self.state == "game":
            current_time = pygame.time.get_ticks()
            if current_time - self.last_time >= 1000:  # 1 second passed
                self.timer -= 1
                self.last_time = current_time
                
                if self.timer <= 0:
                    self.state = "game_over"
    
    def handle_game_over_click(self, mouse_pos, menu_button, name_input_rect, submit_button):
        # Name input box: activate for typing
        if name_input_rect and name_input_rect.collidepoint(mouse_pos):
            self.name_input_active = True
            return
        # Submit button: save high score if name entered
        if submit_button and submit_button.collidepoint(mouse_pos) and len(self.player_name) > 0:
            highscores = load_highscores()
            is_high_score = len(highscores[self.difficulty]) < 5 or self.score > min(score["score"] for score in highscores[self.difficulty])
            if is_high_score:
                self.score += self.timer
            update_highscores(self.difficulty, self.player_name, self.score)
            self.state = "menu"
            self.name_input_active = False
            self.player_name = ""
            return
        # Clicked elsewhere: deactivate name input
        self.name_input_active = False
    
    def run(self):
        running = True
        while running:
            mouse_pos = pygame.mouse.get_pos()
            # Process events
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                    if self.state == "menu":
                        buttons = self.draw_menu()
                        self.handle_menu_click(mouse_pos, buttons)
                    elif self.state == "difficulty":
                        buttons = self.draw_difficulty_selection()
                        self.handle_difficulty_click(mouse_pos, buttons)
                    elif self.state == "game":
                        answer_cells, back_button = self.draw_game()
                        self.handle_game_click(mouse_pos, answer_cells, back_button)
                    elif self.state == "game_over":
                        menu_button, name_input_rect, submit_button = self.draw_game_over()
                        self.handle_game_over_click(mouse_pos, menu_button, name_input_rect, submit_button)
                elif event.type == MOUSEBUTTONUP and event.button == 1:
                    if self.state == "game" and self.dragging:
                        answer_cells, _ = self.draw_game()
                        self.handle_mouse_up(mouse_pos, answer_cells)
                elif event.type == KEYDOWN:
                    self.handle_key_down(event.key)
            # Update timer
            self.update_timer()
            # Draw current state
            if self.state == "menu":
                self.draw_menu()
            elif self.state == "difficulty":
                self.draw_difficulty_selection()
            elif self.state == "game":
                self.draw_game()
            elif self.state == "game_over":
                self.draw_game_over()
            pygame.display.update()
            CLOCK.tick(FPS)
            if self.state == "exit_to_launcher":
                running = False



# Entry point for launcher integration
def launch_math_flip(screen_width=None, screen_height=None, fullscreen=True):
    import pygame
    screen = pygame.display.get_surface()
    game = MathFlipGame(screen_width=screen_width, screen_height=screen_height, fullscreen=fullscreen, screen=screen)
    game.run()
