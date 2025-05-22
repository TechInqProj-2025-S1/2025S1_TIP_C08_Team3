# Main game logic
import pygame
from pygame.locals import QUIT, MOUSEBUTTONDOWN, MOUSEBUTTONUP, KEYDOWN, K_BACKSPACE, K_RETURN, K_a, K_z, K_0, K_9, K_SPACE
from .constants import *
from .fonts import FONT_LARGE, FONT_MEDIUM, FONT_SMALL
from .highscore import initialize_highscores, load_highscores, save_highscores, update_highscores
from .question import QuestionGrid

# Main class
class MathFlipGame:
    def __init__(self, screen_width=None, screen_height=None, fullscreen=True, screen=None):
        import os
        import json
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
        self.WINDOW_WIDTH = screen_width
        self.WINDOW_HEIGHT = screen_height
        if screen is not None:
            self.DISPLAYSURF = screen
        else:
            flags = pygame.NOFRAME
            self.DISPLAYSURF = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT), flags)
            pygame.display.set_caption('Math Flip Game')
        self.CLOCK = pygame.time.Clock()
        self.GRID_SIZE = GRID_SIZE
        max_grid_width = int(self.WINDOW_WIDTH * 0.6)
        max_grid_height = int(self.WINDOW_HEIGHT * 0.6)
        self.CELL_SIZE = min(max_grid_width // self.GRID_SIZE, max_grid_height // self.GRID_SIZE)
        self.GRID_PIXEL_SIZE = self.CELL_SIZE * self.GRID_SIZE
        self.GRID_OFFSET_X = (self.WINDOW_WIDTH - self.GRID_PIXEL_SIZE) // 2
        self.GRID_OFFSET_Y = max(70, (self.WINDOW_HEIGHT - self.GRID_PIXEL_SIZE) // 2 - 40)
        self.state = "menu"
        self.difficulty = EASY
        self.score = 0
        # revealed set below
        self.correct_matches = 0
        self.total_matches = 0
        self.selected_cell = None
        self.dragging = False
        self.selected_answer = None
        initialize_highscores()
        self.player_name = ""
        self.name_input_active = False
        self.timer = 60
        self.last_time = pygame.time.get_ticks()
        self.answered_cells = set()
        self.question_grid = None
        self.grid = None
        self.answers = None
        # revealed set in reset_game
        self.reset_game()

    def reset_game(self):
        # Reset all state
        self.revealed = [[False for _ in range(self.GRID_SIZE)] for _ in range(self.GRID_SIZE)]
        self.score = 0
        self.correct_matches = 0
        self.selected_cell = None
        self.selected_answer = None
        self.dragging = False
        self.timer = 60
        self.last_time = pygame.time.get_ticks()
        self.answered_cells = set()
        self._bonus_added = False  # Reset bonus flag
        self._bonus_value = 0
        self.question_grid = QuestionGrid(self.difficulty)
        self.grid = self.question_grid.grid
        self.answers = self.question_grid.answers
        self.total_matches = len([cell for row in self.grid for cell in row if cell is not None])

    # Drawing/UI
    def draw_menu(self):
        surf = self.DISPLAYSURF
        surf.fill(BG_COLOR)
        title = FONT_LARGE.render("Math Flip Game", True, PRIMARY_COLOR)
        title_y = 120
        surf.blit(title, (self.WINDOW_WIDTH//2 - title.get_width()//2, title_y))
        button_width = 240
        button_height = 56
        spacing = 32
        center_x = self.WINDOW_WIDTH // 2
        start_y = title_y + title.get_height() + 60
        play_button = pygame.Rect(center_x - button_width//2, start_y, button_width, button_height)
        pygame.draw.rect(surf, BUTTON_COLOR, play_button, border_radius=16)
        play_text = FONT_MEDIUM.render("Play", True, BUTTON_TEXT_COLOR)
        surf.blit(play_text, (play_button.centerx - play_text.get_width()//2, play_button.centery - play_text.get_height()//2))
        back_button = pygame.Rect(center_x - button_width//2, play_button.bottom + spacing, button_width, button_height)
        pygame.draw.rect(surf, SECONDARY_COLOR, back_button, border_radius=16)
        back_text = FONT_MEDIUM.render("Back to Menu", True, BUTTON_TEXT_COLOR)
        surf.blit(back_text, (back_button.centerx - back_text.get_width()//2, back_button.centery - back_text.get_height()//2))
        return [play_button, back_button]

    def draw_difficulty_selection(self):
        surf = self.DISPLAYSURF
        surf.fill(BG_COLOR)
        title = FONT_LARGE.render("Select Difficulty", True, PRIMARY_COLOR)
        title_y = 100
        surf.blit(title, (self.WINDOW_WIDTH//2 - title.get_width()//2, title_y))
        button_width = 180
        button_height = 48
        spacing = 24
        desc_spacing = 8
        desc_to_button_spacing = 24
        center_x = self.WINDOW_WIDTH // 2
        start_y = title_y + title.get_height() + 48
        button_gap = 32
        desc_gap = 10
        easy_button_y = start_y
        easy_button = pygame.Rect(center_x - button_width//2, easy_button_y, button_width, button_height)
        pygame.draw.rect(surf, ACCENT_COLOR, easy_button, border_radius=12)
        easy_text = FONT_MEDIUM.render("Easy", True, BUTTON_TEXT_COLOR)
        surf.blit(easy_text, (easy_button.centerx - easy_text.get_width()//2, easy_button.centery - easy_text.get_height()//2))
        easy_desc = FONT_SMALL.render("Addition only", True, TEXT_COLOR)
        easy_desc_y = easy_button.bottom + desc_gap
        surf.blit(easy_desc, (center_x - easy_desc.get_width()//2, easy_desc_y))
        normal_button_y = easy_desc_y + easy_desc.get_height() + button_gap
        normal_button = pygame.Rect(center_x - button_width//2, normal_button_y, button_width, button_height)
        pygame.draw.rect(surf, PRIMARY_COLOR, normal_button, border_radius=12)
        normal_text = FONT_MEDIUM.render("Normal", True, BUTTON_TEXT_COLOR)
        surf.blit(normal_text, (normal_button.centerx - normal_text.get_width()//2, normal_button.centery - normal_text.get_height()//2))
        normal_desc = FONT_SMALL.render("Addition and Subtraction", True, TEXT_COLOR)
        normal_desc_y = normal_button.bottom + desc_gap
        surf.blit(normal_desc, (center_x - normal_desc.get_width()//2, normal_desc_y))
        hard_button_y = normal_desc_y + normal_desc.get_height() + button_gap
        hard_button = pygame.Rect(center_x - button_width//2, hard_button_y, button_width, button_height)
        pygame.draw.rect(surf, WARNING_COLOR, hard_button, border_radius=12)
        hard_text = FONT_MEDIUM.render("Hard", True, BUTTON_TEXT_COLOR)
        surf.blit(hard_text, (hard_button.centerx - hard_text.get_width()//2, hard_button.centery - hard_text.get_height()//2))
        hard_desc = FONT_SMALL.render("Addition, Subtraction, Multiplication, Division", True, TEXT_COLOR)
        hard_desc_y = hard_button.bottom + desc_gap
        surf.blit(hard_desc, (center_x - hard_desc.get_width()//2, hard_desc_y))
        bottom_y = hard_desc_y + hard_desc.get_height() + 32
        back_button_width = 120
        back_button_height = 44
        back_button_x = center_x - back_button_width // 2
        back_button_y = bottom_y
        back_button = pygame.Rect(back_button_x, back_button_y, back_button_width, back_button_height)
        pygame.draw.rect(surf, SECONDARY_COLOR, back_button, border_radius=12)
        back_text = FONT_SMALL.render("Back", True, BUTTON_TEXT_COLOR)
        surf.blit(back_text, (back_button.centerx - back_text.get_width()//2, back_button.centery - back_text.get_height()//2))
        return [easy_button, normal_button, hard_button, back_button]

    def draw_game(self):
        surf = self.DISPLAYSURF
        surf.fill(BG_COLOR)
        title = FONT_MEDIUM.render(f"Math Flip Game - {self.difficulty}", True, PRIMARY_COLOR)
        surf.blit(title, (self.WINDOW_WIDTH//2 - title.get_width()//2, 20))
        score_text = FONT_MEDIUM.render(f"Score: {self.score}", True, TEXT_COLOR)
        surf.blit(score_text, (32, 20))
        timer_text = FONT_MEDIUM.render(f"Time: {self.timer}", True, TEXT_COLOR)
        surf.blit(timer_text, (self.WINDOW_WIDTH - 170, 20))
        progress_text = FONT_SMALL.render(f"Matched: {self.correct_matches}/{self.total_matches}", True, TEXT_COLOR)
        surf.blit(progress_text, (self.WINDOW_WIDTH//2 - progress_text.get_width()//2, 54))
        answer_cells = []
        for i in range(self.GRID_SIZE):
            for j in range(self.GRID_SIZE):
                cell_rect = pygame.Rect(
                    self.GRID_OFFSET_X + j * self.CELL_SIZE,
                    self.GRID_OFFSET_Y + i * self.CELL_SIZE,
                    self.CELL_SIZE,
                    self.CELL_SIZE
                )
                if self.revealed[i][j] and (i, j) in getattr(self, 'answered_cells', set()):
                    color = ACCENT_COLOR
                elif self.revealed[i][j]:
                    color = PRIMARY_COLOR
                else:
                    color = GRAY
                pygame.draw.rect(surf, color, cell_rect, border_radius=12)
                pygame.draw.rect(surf, SECONDARY_COLOR, cell_rect, 2, border_radius=12)
                if self.revealed[i][j] and (i, j) not in getattr(self, 'answered_cells', set()):
                    # Check grid structure
                    if self.grid and isinstance(self.grid, list) and i < len(self.grid) and j < len(self.grid[i]) and self.grid[i][j] is not None:
                        if self.selected_cell == (i, j) and self.dragging:
                            pass
                        else:
                            cell_value = self.grid[i][j]
                            if cell_value is not None and isinstance(cell_value, (list, tuple)) and len(cell_value) > 0 and cell_value[0] is not None:
                                question_text = FONT_SMALL.render(str(cell_value[0]), True, WHITE)
                                if question_text:
                                    surf.blit(question_text, (cell_rect.centerx - question_text.get_width()//2, cell_rect.centery - question_text.get_height()//2))
        if self.dragging and self.selected_cell is not None:
            i, j = self.selected_cell
            cell_value = self.grid[i][j] if self.grid and self.grid[i][j] is not None else None
            if cell_value is not None and isinstance(cell_value, (list, tuple)) and len(cell_value) > 0 and cell_value[0] is not None:
                mouse_pos = pygame.mouse.get_pos()
                hover_on_answer = False
                hover_rect = None
                if self.answers and len(self.answers) > 0:
                    answer_bar_width = min(self.WINDOW_WIDTH - 40, self.GRID_PIXEL_SIZE)
                    answer_width = answer_bar_width // len(self.answers)
                    answer_bar_x = (self.WINDOW_WIDTH - answer_bar_width) // 2
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
                        qrect = question_text.get_rect(midbottom=(hover_rect.centerx, hover_rect.top - 8))
                        pygame.draw.rect(surf, PRIMARY_COLOR, qrect.inflate(20, 10), border_radius=10)
                        pygame.draw.rect(surf, SECONDARY_COLOR, qrect.inflate(20, 10), 2, border_radius=10)
                        surf.blit(question_text, qrect)
                    else:
                        question_rect = question_text.get_rect(center=mouse_pos)
                        pygame.draw.rect(surf, PRIMARY_COLOR, question_rect.inflate(20, 10), border_radius=10)
                        pygame.draw.rect(surf, SECONDARY_COLOR, question_rect.inflate(20, 10), 2, border_radius=10)
                        surf.blit(question_text, question_rect)
        if self.answers and len(self.answers) > 0:
            answer_bar_width = min(self.WINDOW_WIDTH - 40, self.GRID_PIXEL_SIZE)
            answer_width = answer_bar_width // len(self.answers)
            answer_bar_x = (self.WINDOW_WIDTH - answer_bar_width) // 2
            answer_bar_y = self.GRID_OFFSET_Y + self.GRID_PIXEL_SIZE + 40
            for i, answer in enumerate(self.answers):
                cell_rect = pygame.Rect(
                    answer_bar_x + i * answer_width,
                    answer_bar_y,
                    answer_width,
                    ANSWER_CELL_HEIGHT
                )
                cell_color = ACCENT_COLOR if self.selected_answer == i else PRIMARY_COLOR
                pygame.draw.rect(surf, cell_color, cell_rect, border_radius=14)
                pygame.draw.rect(surf, SECONDARY_COLOR, cell_rect, 2, border_radius=14)
                answer_text = FONT_MEDIUM.render(str(answer), True, WHITE)
                if answer_text:
                    surf.blit(answer_text, (cell_rect.centerx - answer_text.get_width()//2, cell_rect.centery - answer_text.get_height()//2))
                answer_cells.append(cell_rect)
        back_button = pygame.Rect(32, self.WINDOW_HEIGHT - 70, 120, 44)
        pygame.draw.rect(surf, BUTTON_COLOR, back_button, border_radius=12)
        back_text = FONT_SMALL.render("Menu", True, BUTTON_TEXT_COLOR)
        surf.blit(back_text, (back_button.centerx - back_text.get_width()//2, back_button.centery - back_text.get_height()//2))
        return answer_cells, back_button

    def draw_game_over(self):
        surf = self.DISPLAYSURF
        surf.fill(WHITE)
        title = FONT_LARGE.render("Game Over!", True, BLUE)
        surf.blit(title, (self.WINDOW_WIDTH//2 - title.get_width()//2, 100))
        # Add bonus once
        if not self._bonus_added:
            self._bonus_value = self.timer if self.timer > 0 else 0
            self.score += self._bonus_value
            self._bonus_added = True
        bonus = self._bonus_value
        if bonus > 0:
            bonus_text = FONT_MEDIUM.render(f"Bonus for time left: +{bonus}", True, (0, 128, 0))
            surf.blit(bonus_text, (self.WINDOW_WIDTH//2 - bonus_text.get_width()//2, 160))
            score_y = 200
        else:
            score_y = 200
        score_text = FONT_LARGE.render(f"Your Score: {self.score}", True, BLACK)
        surf.blit(score_text, (self.WINDOW_WIDTH//2 - score_text.get_width()//2, score_y))
        highscores = load_highscores()
        scores_list = highscores.get(self.difficulty, [])
        is_high_score = (len(scores_list) < 5 or (scores_list and self.score > min(score["score"] for score in scores_list)))
        name_input_rect = None
        submit_button = None
        if is_high_score:
            prompt_text = FONT_MEDIUM.render("New High Score! Enter your name:", True, BLACK)
            surf.blit(prompt_text, (self.WINDOW_WIDTH//2 - prompt_text.get_width()//2, 280))
            name_input_rect = pygame.Rect(self.WINDOW_WIDTH//2 - 150, 330, 300, 40)
            pygame.draw.rect(surf, WHITE, name_input_rect, border_radius=10)
            pygame.draw.rect(surf, BLACK, name_input_rect, 2, border_radius=10)
            name_text = FONT_MEDIUM.render(self.player_name, True, BLACK)
            surf.blit(name_text, (name_input_rect.x + 10, name_input_rect.centery - name_text.get_height()//2))
            if len(self.player_name) > 0:
                submit_button = pygame.Rect(self.WINDOW_WIDTH//2 - 75, 390, 150, 44)
                pygame.draw.rect(surf, PRIMARY_COLOR, submit_button, border_radius=10)
                pygame.draw.rect(surf, ACCENT_COLOR, submit_button, 2, border_radius=10)
                submit_text = FONT_MEDIUM.render("Submit", True, WHITE)
                surf.blit(submit_text, (submit_button.centerx - submit_text.get_width()//2, submit_button.centery - submit_text.get_height()//2))
        return None, name_input_rect, submit_button

    # Events
    def handle_menu_click(self, mouse_pos, buttons):
        for i, button in enumerate(buttons):
            if button.collidepoint(mouse_pos):
                if i == 0:
                    self.state = "difficulty"
                elif i == 1:
                    self.state = "exit_to_launcher"

    def handle_difficulty_click(self, mouse_pos, buttons):
        for i, button in enumerate(buttons):
            if button.collidepoint(mouse_pos):
                if i == 0:
                    self.difficulty = EASY
                    self.reset_game()
                    self.state = "game"
                elif i == 1:
                    self.difficulty = NORMAL
                    self.reset_game()
                    self.state = "game"
                elif i == 2:
                    self.difficulty = HARD
                    self.reset_game()
                    self.state = "game"
                elif i == 3:
                    self.state = "menu"

    def handle_game_click(self, mouse_pos, answer_cells, back_button):
        if back_button and back_button.collidepoint(mouse_pos):
            self.state = "menu"
            return
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
                    if not self.revealed[i][j]:
                        for x in range(self.GRID_SIZE):
                            for y in range(self.GRID_SIZE):
                                if self.revealed[x][y] and (x, y) not in getattr(self, 'answered_cells', set()):
                                    self.revealed[x][y] = False
                        self.revealed[i][j] = True
                        self.selected_cell = (i, j)
                        self.dragging = False
                        return
                    elif (i, j) not in getattr(self, 'answered_cells', set()) and self.revealed[i][j]:
                        self.selected_cell = (i, j)
                        self.dragging = True
                        return

    def handle_mouse_up(self, mouse_pos, answer_cells):
        if self.dragging and self.selected_cell is not None:
            i, j = self.selected_cell
            # Check grid structure
            cell_value = None
            if self.grid and isinstance(self.grid, list) and i < len(self.grid) and j < len(self.grid[i]):
                cell_value = self.grid[i][j]
            if cell_value is not None and isinstance(cell_value, (list, tuple)) and len(cell_value) == 2:
                question, correct_answer = cell_value
                if not answer_cells:
                    answer_cells = []
                # Ensure answer_cells is list
                answer_cells_list = answer_cells if isinstance(answer_cells, list) else []
                for answer_idx, cell in enumerate(answer_cells_list):
                    if cell.collidepoint(mouse_pos):
                        selected_answer = None
                        if self.answers and isinstance(self.answers, list) and answer_idx < len(self.answers):
                            selected_answer = self.answers[answer_idx]
                        if not hasattr(self, 'answered_cells'):
                            self.answered_cells = set()
                        # Check answers list
                        answers_slice = self.answers[:-1] if self.answers and isinstance(self.answers, list) and len(self.answers) > 0 else []
                        if (selected_answer == "Other" and correct_answer not in answers_slice) or (selected_answer == correct_answer):
                            self.score += 10
                            self.correct_matches += 1
                            self.answered_cells.add((i, j))
                            self.timer += 5
                        else:
                            self.score = max(0, self.score - 5)
                            self.timer = max(1, self.timer - 3)
                        break
            self.dragging = False
            self.selected_cell = None
            if hasattr(self, 'answered_cells') and self.correct_matches >= self.total_matches:
                self.score += self.timer * 2
                self.state = "game_over"

    def handle_key_down(self, key):
        if self.state == "game_over" and self.name_input_active:
            if key == K_BACKSPACE:
                self.player_name = self.player_name[:-1]
            elif key == K_RETURN and len(self.player_name) > 0:
                highscores = load_highscores()
                scores_list = highscores.get(self.difficulty, [])
                is_high_score = (len(scores_list) < 5 or (scores_list and self.score > min(score["score"] for score in scores_list)))
                if is_high_score:
                    # Add timer bonus once
                    if not self._bonus_added:
                        self.score += self.timer
                        self._bonus_added = True
                    update_highscores(self.difficulty, self.player_name, self.score)
                self.state = "menu"
                self.name_input_active = False
                self.player_name = ""
            elif len(self.player_name) < 10 and (key in range(K_a, K_z + 1) or key in range(K_0, K_9 + 1) or key == K_SPACE):
                self.player_name += chr(key).upper()

    def update_timer(self):
        if self.state == "game":
            current_time = pygame.time.get_ticks()
            if current_time - self.last_time >= 1000:
                self.timer -= 1
                self.last_time = current_time
                if self.timer <= 0:
                    self.state = "game_over"

    def handle_game_over_click(self, mouse_pos, menu_button, name_input_rect, submit_button):
        if name_input_rect and name_input_rect.collidepoint(mouse_pos):
            self.name_input_active = True
            return
        if submit_button and submit_button.collidepoint(mouse_pos) and len(self.player_name) > 0:
            highscores = load_highscores()
            is_high_score = len(highscores[self.difficulty]) < 5 or self.score > min(score["score"] for score in highscores[self.difficulty])
            if is_high_score:
                # Add timer bonus once
                if not self._bonus_added:
                    self.score += self.timer
                    self._bonus_added = True
            update_highscores(self.difficulty, self.player_name, self.score)
            self.state = "menu"
            self.name_input_active = False
            self.player_name = ""
            return
        self.name_input_active = False

    def run(self):
        running = True
        while running:
            mouse_pos = pygame.mouse.get_pos()
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
            self.update_timer()
            if self.state == "menu":
                self.draw_menu()
            elif self.state == "difficulty":
                self.draw_difficulty_selection()
            elif self.state == "game":
                self.draw_game()
            elif self.state == "game_over":
                self.draw_game_over()
            pygame.display.update()
            self.CLOCK.tick(FPS)
            if self.state == "exit_to_launcher":
                running = False
