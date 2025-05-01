import pygame
import random
import os
import json

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 900  # Increased width for more space
SCREEN_HEIGHT = 700  # Increased height for more space
GRID_SIZE = 26  # Slightly smaller blocks for more breathing room
GRID_WIDTH = 10
GRID_HEIGHT = 20
SIDEBAR_WIDTH = 240  # Wider sidebar for better spacing

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

# THEME CONSTANTS (should match launcher)
PRIMARY_COLOR = (52, 152, 219)  # Blue
SECONDARY_COLOR = (41, 128, 185)  # Darker Blue
ACCENT_COLOR = (46, 204, 113)  # Green
WARNING_COLOR = (231, 76, 60)  # Red
BG_COLOR = (236, 240, 241)  # Light Gray
TEXT_COLOR = (44, 62, 80)  # Dark Gray
BLOCK_COLORS = [PRIMARY_COLOR, SECONDARY_COLOR, ACCENT_COLOR, WARNING_COLOR, (241, 196, 15), (155, 89, 182), (230, 126, 34)]
TITLE_FONT = pygame.font.SysFont('arial', 60, bold=True)
BODY_FONT = pygame.font.SysFont('arial', 32)
SCORE_FONT = pygame.font.SysFont('arial', 28)

# Tetromino shapes
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[1, 1, 1], [0, 1, 0]],  # T
    [[1, 1, 1], [1, 0, 0]],  # J
    [[1, 1, 1], [0, 0, 1]],  # L
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 1, 0], [0, 1, 1]]   # Z
]

# Colors for each shape
SHAPE_COLORS = [CYAN, YELLOW, MAGENTA, BLUE, ORANGE, GREEN, RED]

class MathProblem:
    def __init__(self, difficulty=1):
        self.difficulty = difficulty
        self.user_answer = ""
        self.answered = False
        self.correct = False
        self.problem_type = None
        self.generate_problem()

    def generate_problem(self):
        # Define problem types and their logic
        problem_types = ["add", "sub", "mul", "div", "equation"]
        # Increase variety as difficulty increases
        if self.difficulty == 1:
            types = ["add", "sub"]
        elif self.difficulty == 2:
            types = ["add", "sub", "mul"]
        elif self.difficulty == 3:
            types = ["add", "sub", "mul", "div"]
        else:
            types = problem_types
        self.problem_type = random.choice(types)
        if self.problem_type == "add":
            a = random.randint(1, 20 * self.difficulty)
            b = random.randint(1, 20 * self.difficulty)
            self.equation = f"{a} + {b} = ?"
            self.answer = a + b
        elif self.problem_type == "sub":
            a = random.randint(1, 20 * self.difficulty)
            b = random.randint(1, a)
            self.equation = f"{a} - {b} = ?"
            self.answer = a - b
        elif self.problem_type == "mul":
            a = random.randint(2, 10 * self.difficulty)
            b = random.randint(2, 10 * self.difficulty)
            self.equation = f"{a} × {b} = ?"
            self.answer = a * b
        elif self.problem_type == "div":
            b = random.randint(2, 10 * self.difficulty)
            self.answer = random.randint(2, 10 * self.difficulty)
            a = self.answer * b
            self.equation = f"{a} ÷ {b} = ?"
        elif self.problem_type == "equation":
            # Solve for x: ax + b = c
            a = random.randint(1, 10 * self.difficulty)
            x = random.randint(1, 10 * self.difficulty)
            b = random.randint(0, 10 * self.difficulty)
            c = a * x + b
            self.equation = f"{a}x + {b} = {c}; x = ?"
            self.answer = x

    def check_answer(self, user_input):
        try:
            user_value = int(user_input)
            self.correct = (user_value == self.answer)
            self.answered = True
            return self.correct
        except ValueError:
            return False

    def add_digit(self, digit):
        if len(self.user_answer) < 7:  # Allow longer answers
            self.user_answer += digit

    def remove_digit(self):
        if self.user_answer:
            self.user_answer = self.user_answer[:-1]

    def reset(self, difficulty=None):
        if difficulty is not None:
            self.difficulty = difficulty
        self.generate_problem()
        self.user_answer = ""
        self.answered = False
        self.correct = False

class Tetromino:
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = SHAPE_COLORS[SHAPES.index(shape)]
        self.rotation = 0

    def rotate(self):
        self.rotation = (self.rotation + 1) % 4
        self.shape = self.get_rotated_shape()
        
    def get_rotated_shape(self):
        if self.shape is not None:
            if self.rotation == 0:
                return self.shape
            elif self.rotation == 1:
                # Rotate 90 degrees
                rows = len(self.shape)
                cols = len(self.shape[0])
                rotated = [[0 for _ in range(rows)] for _ in range(cols)]
                for r in range(rows):
                    for c in range(cols):
                        rotated[c][rows - 1 - r] = self.shape[r][c]
                return rotated
            elif self.rotation == 2:
                # Rotate 180 degrees
                rows = len(self.shape)
                cols = len(self.shape[0])
                rotated = [[0 for _ in range(cols)] for _ in range(rows)]
                for r in range(rows):
                    for c in range(cols):
                        rotated[rows - 1 - r][cols - 1 - c] = self.shape[r][c]
                return rotated
            elif self.rotation == 3:
                # Rotate 270 degrees
                rows = len(self.shape)
                cols = len(self.shape[0])
                rotated = [[0 for _ in range(rows)] for _ in range(cols)]
                for r in range(rows):
                    for c in range(cols):
                        rotated[cols - 1 - c][r] = self.shape[r][c]
                return rotated

class TetrisGame:
    def __init__(self):
        # Responsive: get display size or use default
        info = pygame.display.Info()
        global SCREEN_WIDTH, SCREEN_HEIGHT
        SCREEN_WIDTH, SCREEN_HEIGHT = info.current_w, info.current_h
        # Set a minimum size for playability
        SCREEN_WIDTH = max(SCREEN_WIDTH, 800)
        SCREEN_HEIGHT = max(SCREEN_HEIGHT, 600)
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Tetris Math")
        # Responsive grid size
        self.grid_height = 20
        self.grid_width = 10
        # Calculate grid size to fit vertically with some margin
        self.grid_size = min((SCREEN_HEIGHT - 80) // self.grid_height, (SCREEN_WIDTH - 400) // self.grid_width)
        self.grid_left = 60
        self.grid_top = (SCREEN_HEIGHT - self.grid_height * self.grid_size) // 2
        self.sidebar_width = max(220, SCREEN_WIDTH - (self.grid_left + self.grid_width * self.grid_size + 60))
        self.sidebar_left = self.grid_left + self.grid_width * self.grid_size + 40
        self.sidebar_top = self.grid_top
        # Responsive fonts
        font_size = max(18, int(self.grid_size * 1.2))
        large_font_size = max(28, int(self.grid_size * 1.8))
        self.font = pygame.font.SysFont('Arial', font_size)
        self.large_font = pygame.font.SysFont('Arial', large_font_size)
        global TITLE_FONT, BODY_FONT, SCORE_FONT
        TITLE_FONT = pygame.font.SysFont('arial', int(self.grid_size * 2.3), bold=True)
        BODY_FONT = pygame.font.SysFont('arial', int(self.grid_size * 1.2))
        SCORE_FONT = pygame.font.SysFont('arial', int(self.grid_size * 1.0))
        self.clock = pygame.time.Clock()
        self.grid = [[0 for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.game_over = False
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.fall_speed = 0.5  # seconds per step
        self.fall_time = 0
        self.math_problem = MathProblem(difficulty=1)
        self.piece_locked = True
        self.correct_answers = 0
        self.math_feedback_time = 0
        self.show_math_feedback = False
        self.hold_piece = None
        self.hold_used = False
        self.move_left_pressed = False
        self.move_right_pressed = False
        self.move_down_pressed = False
        self.move_delay = 120  # ms before repeat
        self.move_interval = 50  # ms between repeats
        self.last_move_time = 0
        self.last_dir = 0
        self.pieces_since_question = 0
        self.math_question_active = False
        self.player_name = self.prompt_player_name()
        self.state = "playing"  # 'playing', 'math_challenge', 'feedback', 'game_over'
        self.feedback_message = ""
        self.feedback_color = ACCENT_COLOR
        self.debug = True  # Enable debug mode for verbose console output
        
    def prompt_player_name(self):
        # Simple text input prompt before game starts
        name = ""
        input_active = True
        font = pygame.font.SysFont('Arial', 36)
        difficulty = None
        easy_button = pygame.Rect(SCREEN_WIDTH // 2 - 160, SCREEN_HEIGHT // 2 + 80, 140, 50)
        hard_button = pygame.Rect(SCREEN_WIDTH // 2 + 20, SCREEN_HEIGHT // 2 + 80, 140, 50)
        while input_active:
            self.screen.fill(BG_COLOR)
            prompt = font.render("Enter your name:", True, TEXT_COLOR)
            self.screen.blit(prompt, (SCREEN_WIDTH // 2 - prompt.get_width() // 2, SCREEN_HEIGHT // 2 - 60))
            name_surface = font.render(name, True, ACCENT_COLOR)
            input_box = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2, 300, 50)
            pygame.draw.rect(self.screen, WHITE, input_box, 2)
            name_rect = name_surface.get_rect()
            name_rect.midleft = (input_box.x + 10, input_box.y + input_box.height // 2)
            self.screen.blit(name_surface, name_rect)
            instr = SCORE_FONT.render("Press Enter to start", True, TEXT_COLOR)
            self.screen.blit(instr, (SCREEN_WIDTH // 2 - instr.get_width() // 2, SCREEN_HEIGHT // 2 + 70))
            # Draw difficulty buttons
            pygame.draw.rect(self.screen, ACCENT_COLOR if difficulty == 'easy' else WHITE, easy_button, border_radius=8)
            pygame.draw.rect(self.screen, ACCENT_COLOR if difficulty == 'hard' else WHITE, hard_button, border_radius=8)
            easy_text = SCORE_FONT.render("Easy", True, TEXT_COLOR)
            hard_text = SCORE_FONT.render("Hard", True, TEXT_COLOR)
            self.screen.blit(easy_text, (easy_button.x + (easy_button.width - easy_text.get_width()) // 2, easy_button.y + 10))
            self.screen.blit(hard_text, (hard_button.x + (hard_button.width - hard_text.get_width()) // 2, hard_button.y + 10))
            diff_instr = SCORE_FONT.render("Choose difficulty:", True, TEXT_COLOR)
            self.screen.blit(diff_instr, (SCREEN_WIDTH // 2 - diff_instr.get_width() // 2, SCREEN_HEIGHT // 2 + 40))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and name and difficulty:
                        input_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        name = name[:-1]
                    elif len(name) < 12 and event.unicode.isprintable():
                        name += event.unicode
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    if easy_button.collidepoint(mx, my):
                        difficulty = 'easy'
                    elif hard_button.collidepoint(mx, my):
                        difficulty = 'hard'
        self.difficulty_mode = difficulty
        return name

    def new_piece(self):
        shape = random.choice(SHAPES)
        return Tetromino(self.grid_width // 2 - len(shape[0]) // 2, 0, shape)
    
    def valid_move(self, piece, x, y, shape=None):
        if shape is None:
            shape = piece.shape
            
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell:
                    if (x + j < 0 or x + j >= self.grid_width or 
                        y + i >= self.grid_height or
                        (y + i >= 0 and self.grid[y + i][x + j])):
                        return False
        return True
    
    def add_to_grid(self, piece):
        for i, row in enumerate(piece.shape):
            for j, cell in enumerate(row):
                if cell:
                    if piece.y + i >= 0:  # Only add to grid if it's visible
                        self.grid[piece.y + i][piece.x + j] = piece.color
    
    def clear_lines(self):
        lines_to_clear = []
        for i, row in enumerate(self.grid):
            if all(cell != 0 for cell in row):
                lines_to_clear.append(i)
        
        for line in lines_to_clear:
            # Move all lines above this one down
            for y in range(line, 0, -1):
                self.grid[y] = self.grid[y-1][:]
            # Add empty line at top
            self.grid[0] = [0 for _ in range(self.grid_width)]
        
        # Update score
        num_lines = len(lines_to_clear)
        if num_lines > 0:
            self.lines_cleared += num_lines
            self.score += [100, 300, 500, 800][min(num_lines-1, 3)] * self.level
            self.level = self.lines_cleared // 10 + 1
            self.fall_speed = max(0.05, 0.5 - (self.level - 1) * 0.05)
    
    def draw_grid(self):
        # Use responsive positions
        grid_left = self.grid_left
        grid_top = self.grid_top
        grid_size = self.grid_size
        
        # Draw the background
        self.screen.fill(BG_COLOR)
        
        # Draw the grid
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                pygame.draw.rect(self.screen, GRAY, 
                                 (grid_left + x * grid_size, 
                                  grid_top + y * grid_size, 
                                  grid_size, grid_size), 1)
                if self.grid[y][x]:
                    pygame.draw.rect(self.screen, self.grid[y][x], 
                                     (grid_left + x * grid_size + 1, 
                                      grid_top + y * grid_size + 1, 
                                      grid_size - 2, grid_size - 2))
        
        # Draw the shadow (ghost) piece
        if self.current_piece and self.current_piece.shape is not None:
            ghost_y = self.current_piece.y
            # Find the lowest y the piece can go
            while self.valid_move(self.current_piece, self.current_piece.x, ghost_y + 1):
                ghost_y += 1
            # Draw the ghost piece (outline or translucent)
            for i, row in enumerate(self.current_piece.shape):
                for j, cell in enumerate(row):
                    if cell:
                        # Use a light gray or translucent color for the shadow
                        shadow_color = (180, 180, 180, 120)  # RGBA for translucency
                        rect = pygame.Rect(
                            grid_left + (self.current_piece.x + j) * grid_size + 1,
                            grid_top + (ghost_y + i) * grid_size + 1,
                            grid_size - 2, grid_size - 2)
                        # Draw as outline if surface doesn't support alpha
                        if self.screen.get_bitsize() == 32:
                            s = pygame.Surface((grid_size - 2, grid_size - 2), pygame.SRCALPHA)
                            s.fill(shadow_color)
                            self.screen.blit(s, rect.topleft)
                        else:
                            pygame.draw.rect(self.screen, (180, 180, 180), rect, 2)
        
        # Draw the current piece
        if self.current_piece and self.current_piece.shape is not None:
            for i, row in enumerate(self.current_piece.shape):
                for j, cell in enumerate(row):
                    if cell:
                        color = self.current_piece.color
                        if self.piece_locked:
                            color = tuple(max(0, c - 100) for c in color)
                        pygame.draw.rect(self.screen, color, 
                                        (grid_left + (self.current_piece.x + j) * grid_size + 1, 
                                         grid_top + (self.current_piece.y + i) * grid_size + 1, 
                                         grid_size - 2, grid_size - 2))
        
        # Draw sidebar
        sidebar_left = self.sidebar_left
        sidebar_top = self.sidebar_top
        # Draw score
        score_text = SCORE_FONT.render(f"Score: {self.score}", True, TEXT_COLOR)
        self.screen.blit(score_text, (sidebar_left + 10, sidebar_top + 20))
        
        # Draw level
        level_text = SCORE_FONT.render(f"Level: {self.level}", True, TEXT_COLOR)
        self.screen.blit(level_text, (sidebar_left + 10, sidebar_top + 70))
        
        # Draw lines cleared
        lines_text = SCORE_FONT.render(f"Lines: {self.lines_cleared}", True, TEXT_COLOR)
        self.screen.blit(lines_text, (sidebar_left + 10, sidebar_top + 120))
        
        # Draw math score
        math_score_text = SCORE_FONT.render(f"Math Answers: {self.correct_answers}", True, TEXT_COLOR)
        self.screen.blit(math_score_text, (sidebar_left + 10, sidebar_top + 170))
        
        # Draw next piece
        next_text = SCORE_FONT.render("Next Piece:", True, TEXT_COLOR)
        self.screen.blit(next_text, (sidebar_left + 10, sidebar_top + 230))
        
        # Draw the next piece preview
        next_left = sidebar_left + 40
        next_top = sidebar_top + 270
        if self.next_piece.shape is not None:
            for i, row in enumerate(self.next_piece.shape):
                for j, cell in enumerate(row):
                    if cell:
                        pygame.draw.rect(self.screen, self.next_piece.color, 
                                         (next_left + j * (grid_size - 4), 
                                          next_top + i * (grid_size - 4), 
                                          grid_size - 4, grid_size - 4))
        
        # Draw hold piece
        hold_text = SCORE_FONT.render("Hold:", True, TEXT_COLOR)
        self.screen.blit(hold_text, (self.sidebar_left + 10, self.sidebar_top + 350))
        hold_left = self.sidebar_left + 40
        hold_top = self.sidebar_top + 390
        if self.hold_piece and self.hold_piece.shape is not None:
            for i, row in enumerate(self.hold_piece.shape):
                for j, cell in enumerate(row):
                    if cell:
                        pygame.draw.rect(self.screen, self.hold_piece.color,
                                         (hold_left + j * (self.grid_size - 4),
                                          hold_top + i * (self.grid_size - 4),
                                          self.grid_size - 4, self.grid_size - 4))
        
        # Show feedback for math answers
        if self.show_math_feedback:
            if self.math_problem.correct:
                feedback_text = TITLE_FONT.render("Correct!", True, ACCENT_COLOR)
            else:
                feedback_text = TITLE_FONT.render(f"Wrong! Answer: {self.math_problem.answer}", True, WARNING_COLOR)
            self.screen.blit(feedback_text, (SCREEN_WIDTH // 2 - feedback_text.get_width() // 2, int(grid_top * 0.7)))
                
        # Draw game over if needed
        if self.game_over:
            font = pygame.font.SysFont('Arial', int(self.grid_size * 2.2))
            game_over_text = font.render("GAME OVER", True, WARNING_COLOR)
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(game_over_text, text_rect)
            
            restart_text = BODY_FONT.render("Press R to Restart", True, TEXT_COLOR)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + int(self.grid_size * 2.5)))
            self.screen.blit(restart_text, restart_rect)
        
        # Draw inline math bar at the top
        if self.math_question_active:
            bar_height = int(self.grid_size * 2.2)
            bar_rect = pygame.Rect(0, 0, SCREEN_WIDTH, bar_height)
            pygame.draw.rect(self.screen, PRIMARY_COLOR, bar_rect)
            pygame.draw.rect(self.screen, TEXT_COLOR, bar_rect, 3)
            eq_text = BODY_FONT.render(f"Math Challenge: {self.math_problem.equation}", True, TEXT_COLOR)
            ans_text = BODY_FONT.render(self.math_problem.user_answer, True, ACCENT_COLOR if self.math_problem.correct else WARNING_COLOR)
            self.screen.blit(eq_text, (20, bar_rect.centery - eq_text.get_height() // 2))
            self.screen.blit(ans_text, (SCREEN_WIDTH - 40 - ans_text.get_width(), bar_rect.centery - ans_text.get_height() // 2))
            instr_text = SCORE_FONT.render("Type answer and press Enter", True, TEXT_COLOR)
            self.screen.blit(instr_text, (SCREEN_WIDTH//2 - instr_text.get_width()//2, bar_rect.bottom - instr_text.get_height() - 4))
    
    def reset_game(self):
        self.grid = [[0 for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.game_over = False
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.fall_speed = 0.5
        self.correct_answers = 0
        self.math_problem.reset()
        self.piece_locked = False
        self.hold_used = False
        self.pieces_since_question = 0
        self.math_question_active = False
        self.set_state("playing")
        
    def trigger_math_challenge(self):
        self.math_problem.reset()
        self.set_state("math_challenge")
        self.piece_locked = True

    def show_math_modal(self):
        # Draw a centered modal for the math challenge
        modal_w, modal_h = 500, 220
        modal_x = (SCREEN_WIDTH - modal_w) // 2
        modal_y = (SCREEN_HEIGHT - modal_h) // 2
        modal_rect = pygame.Rect(modal_x, modal_y, modal_w, modal_h)
        pygame.draw.rect(self.screen, WHITE, modal_rect, border_radius=16)
        pygame.draw.rect(self.screen, PRIMARY_COLOR, modal_rect, 4, border_radius=16)
        # Question
        eq_text = BODY_FONT.render(f"{self.math_problem.equation}", True, TEXT_COLOR)
        self.screen.blit(eq_text, (modal_x + 30, modal_y + 30))
        # Input
        ans_text = BODY_FONT.render(self.math_problem.user_answer or "_", True, ACCENT_COLOR)
        self.screen.blit(ans_text, (modal_x + 30, modal_y + 80))
        # Instructions
        instr = SCORE_FONT.render("Type answer and press Enter", True, TEXT_COLOR)
        self.screen.blit(instr, (modal_x + 30, modal_y + 140))

    def show_feedback_modal(self):
        # Draw a centered modal for feedback
        modal_w, modal_h = 400, 120
        modal_x = (SCREEN_WIDTH - modal_w) // 2
        modal_y = (SCREEN_HEIGHT - modal_h) // 2
        modal_rect = pygame.Rect(modal_x, modal_y, modal_w, modal_h)
        pygame.draw.rect(self.screen, WHITE, modal_rect, border_radius=16)
        pygame.draw.rect(self.screen, self.feedback_color, modal_rect, 4, border_radius=16)
        msg = BODY_FONT.render(self.feedback_message, True, self.feedback_color)
        self.screen.blit(msg, (modal_x + 30, modal_y + 40))

    def update(self, dt):
        if self.state == "game_over":
            return
        if self.state == "feedback":
            self.piece_locked = True
            self.math_feedback_time -= dt
            if self.math_feedback_time <= 0:
                self.set_state("playing")
                self.piece_locked = False
        elif self.state == "math_challenge":
            # Easy: pause piece; Hard: piece keeps falling
            if self.difficulty_mode == 'hard':
                self.piece_locked = False
                self.fall_time += dt
                if self.fall_time >= self.fall_speed:
                    self.fall_time = 0
                    if self.valid_move(self.current_piece, self.current_piece.x, self.current_piece.y + 1):
                        self.current_piece.y += 1
                    else:
                        self.add_to_grid(self.current_piece)
                        self.clear_lines()
                        self.pieces_since_question += 1
                        self.current_piece = self.next_piece
                        self.next_piece = self.new_piece()
                        # Don't trigger another math challenge here
                        if not self.valid_move(self.current_piece, self.current_piece.x, self.current_piece.y):
                            self.set_state("game_over")
                            self.game_over = True
            else:
                self.piece_locked = True
        elif self.state == "playing":
            self.piece_locked = False
            self.fall_time += dt
            if self.fall_time >= self.fall_speed:
                self.fall_time = 0
                if self.valid_move(self.current_piece, self.current_piece.x, self.current_piece.y + 1):
                    self.current_piece.y += 1
                else:
                    self.add_to_grid(self.current_piece)
                    self.clear_lines()
                    self.pieces_since_question += 1
                    self.current_piece = self.next_piece
                    self.next_piece = self.new_piece()
                    if self.pieces_since_question >= 5:
                        self.trigger_math_challenge()
                        self.pieces_since_question = 0
            if not self.valid_move(self.current_piece, self.current_piece.x, self.current_piece.y):
                self.set_state("game_over")
                self.game_over = True

    def run(self):
        running = True
        score_saved = False  # Track if score has been saved for this game over
        while running:
            self.clock.tick(60)
            now = pygame.time.get_ticks()
            for event in pygame.event.get():
                if self.debug:
                    print(f"EVENT: {event}")
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if self.debug:
                        print(f"KEYDOWN: {pygame.key.name(event.key)} (unicode: {getattr(event, 'unicode', '')}) state: {self.state}")
                    if self.state == "math_challenge":
                        if event.key in [pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]:
                            self.math_problem.add_digit(event.unicode)
                        elif event.key == pygame.K_BACKSPACE:
                            self.math_problem.remove_digit()
                        elif event.key == pygame.K_RETURN:
                            if self.math_problem.user_answer:
                                correct = self.math_problem.check_answer(self.math_problem.user_answer)
                                if correct:
                                    self.correct_answers += 1
                                    self.feedback_message = "Correct!"
                                    self.feedback_color = ACCENT_COLOR
                                else:
                                    self.feedback_message = f"Wrong! Answer: {self.math_problem.answer}"
                                    self.feedback_color = WARNING_COLOR
                                self.set_state("feedback")
                                self.math_feedback_time = 1.2
                    elif self.state == "playing":
                        if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                            self.move_left_pressed = True
                            self.last_move_time = now
                            self.last_dir = -1
                            self.move_piece(-1)
                        elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                            self.move_right_pressed = True
                            self.last_move_time = now
                            self.last_dir = 1
                            self.move_piece(1)
                        elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                            self.move_down_pressed = True
                            self.soft_drop()
                        elif event.key == pygame.K_UP or event.key == pygame.K_w:
                            self.rotate_piece()
                        elif event.key == pygame.K_SPACE:
                            # Hard drop
                            while self.valid_move(self.current_piece, self.current_piece.x, self.current_piece.y + 1):
                                self.current_piece.y += 1
                                self.score += 1
                        elif event.key == pygame.K_c or event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                            self.hold_current_piece()
                    elif self.state == "game_over":
                        if event.key == pygame.K_r:
                            self.reset_game()
                            score_saved = False
                    if event.key == pygame.K_ESCAPE:
                        running = False
                elif event.type == pygame.KEYUP:
                    if self.debug:
                        print(f"KEYUP: {pygame.key.name(event.key)} state: {self.state}")
                    if self.state == "playing":
                        if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                            self.move_left_pressed = False
                        elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                            self.move_right_pressed = False
                        elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                            self.move_down_pressed = False
            # Key repeat logic
            if self.state == "playing":
                if self.move_left_pressed or self.move_right_pressed:
                    if now - self.last_move_time > self.move_delay:
                        if now % self.move_interval < 16:
                            self.move_piece(self.last_dir)
                if self.move_down_pressed:
                    self.soft_drop()
            if self.debug:
                print(f"move_left_pressed: {self.move_left_pressed}, move_right_pressed: {self.move_right_pressed}, move_down_pressed: {getattr(self, 'move_down_pressed', False)}")
            self.update(self.clock.get_time() / 1000.0)
            self.draw_grid()
            if self.state == "math_challenge":
                self.show_math_modal()
            elif self.state == "feedback":
                self.show_feedback_modal()
            pygame.display.flip()
            if self.state == "game_over" and not score_saved:
                self.save_score()
                score_saved = True
        pygame.quit()
    
    def move_piece(self, dx):
        print(f"move_piece called: dx={dx}, piece_locked={self.piece_locked}, state={self.state}")
        if not self.piece_locked:
            new_x = self.current_piece.x + dx
            print(f"Trying to move to x={new_x}")
            if self.valid_move(self.current_piece, new_x, self.current_piece.y):
                print(f"Move valid. Moving piece from x={self.current_piece.x} to x={new_x}")
                self.current_piece.x = new_x
            else:
                print("Move invalid.")
        else:
            print("Piece is locked, cannot move.")

    def soft_drop(self):
        print(f"soft_drop called: piece_locked={self.piece_locked}, state={self.state}")
        if not self.piece_locked:
            new_y = self.current_piece.y + 1
            print(f"Trying to move to y={new_y}")
            if self.valid_move(self.current_piece, self.current_piece.x, new_y):
                print(f"Move valid. Moving piece from y={self.current_piece.y} to y={new_y}")
                self.current_piece.y = new_y
            else:
                print("Move invalid.")
        else:
            print("Piece is locked, cannot soft drop.")
    
    def rotate_piece(self):
        if not self.piece_locked and self.current_piece.shape is not None:
            rotated_shape = self.current_piece.get_rotated_shape()
            if self.valid_move(self.current_piece, self.current_piece.x, self.current_piece.y, rotated_shape):
                self.current_piece.shape = rotated_shape
                self.current_piece.rotation = (self.current_piece.rotation + 1) % 4
    
    def hold_current_piece(self):
        if not self.hold_used:
            if self.hold_piece is None:
                self.hold_piece = self.current_piece
                self.current_piece = self.next_piece
                self.next_piece = self.new_piece()
            else:
                self.hold_piece, self.current_piece = self.current_piece, self.hold_piece
                if self.current_piece.shape is not None:
                    self.current_piece.x = self.grid_width // 2 - len(self.current_piece.shape[0]) // 2
                    self.current_piece.y = 0
            self.hold_used = True
    
    def lock_piece(self):
        # ...existing code for locking piece...
        self.hold_used = False
        self.update_difficulty()
        self.math_problem.reset(self.math_problem.difficulty)

    def update_difficulty(self):
        # Increase difficulty as score/level increases
        if self.level < 3:
            self.math_problem.difficulty = 1
        elif self.level < 6:
            self.math_problem.difficulty = 2
        elif self.level < 10:
            self.math_problem.difficulty = 3
        else:
            self.math_problem.difficulty = 4

    def save_score(self):
        # Save high score to scores/tetris_math_scores.json
        if not os.path.exists("scores"):
            os.makedirs("scores")
        score_file = "scores/tetris_math_scores.json"
        scores = []
        if os.path.exists(score_file):
            try:
                with open(score_file, 'r') as f:
                    scores = json.load(f)
            except Exception:
                scores = []
        entry = {
            "name": self.player_name,
            "score": self.score,
            "level": self.level,
            "lines_cleared": self.lines_cleared
        }
        scores.append(entry)
        with open(score_file, 'w') as f:
            json.dump(scores, f)

    def set_state(self, new_state):
        # Helper to change state and reset movement flags if leaving 'playing'
        if hasattr(self, 'state') and self.state == 'playing' and new_state != 'playing':
            self.move_left_pressed = False
            self.move_right_pressed = False
            self.move_down_pressed = False
        self.state = new_state

# Main game function
def main():
    game = TetrisGame()
    game.run()

if __name__ == "__main__":
    main()