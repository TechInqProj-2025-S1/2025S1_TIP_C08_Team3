import pygame
import sys
import os
import json
from pygame.locals import QUIT, MOUSEBUTTONDOWN

# Initialize pygame
pygame.init()
pygame.mixer.init()  # For sound effects

# Constants
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 1024
TITLE = "Team 3 Launcher"
FPS = 60

# THEME CONSTANTS
PRIMARY_COLOR = (52, 152, 219)  # Blue
SECONDARY_COLOR = (41, 128, 185)  # Darker Blue
ACCENT_COLOR = (46, 204, 113)  # Green
WARNING_COLOR = (231, 76, 60)  # Red
BG_COLOR = (236, 240, 241)  # Light Gray
TEXT_COLOR = (44, 62, 80)  # Dark Gray
BUTTON_COLOR = PRIMARY_COLOR
BUTTON_HOVER_COLOR = SECONDARY_COLOR
BUTTON_TEXT_COLOR = (255, 255, 255)
TITLE_FONT = pygame.font.SysFont('arial', 60, bold=True)
SUBTITLE_FONT = pygame.font.SysFont('arial', 36, bold=True)
BODY_FONT = pygame.font.SysFont('arial', 32)
SCORE_FONT = pygame.font.SysFont('arial', 28)

# Create the screen in FULLSCREEN mode and get actual monitor size
info = pygame.display.Info()
SCREEN_WIDTH, SCREEN_HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()

# Ensure the scores directory exists
if not os.path.exists("scores"):
    os.makedirs("scores")

class Button:
    def __init__(self, x, y, width, height, text, font_size=BODY_FONT.get_height(), color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR, text_color=BUTTON_TEXT_COLOR):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.text_color = text_color
        self.font = pygame.font.SysFont('arial', font_size, bold=True)
        
    def draw(self, surface):
        pygame.draw.rect(surface, self.current_color, self.rect, border_radius=10)
        pygame.draw.rect(surface, SECONDARY_COLOR, self.rect, 3, border_radius=10)
        
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
    def update(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.current_color = self.hover_color
            return True
        else:
            self.current_color = self.color
            return False
            
    def is_clicked(self, mouse_pos, mouse_click):
        return self.rect.collidepoint(mouse_pos) and mouse_click

class Game:
    def __init__(self, name, description, module_name, class_name=None):
        self.name = name
        self.description = description
        self.module_name = module_name
        self.class_name = class_name
        
    def launch(self):
        try:
            # Dynamic import of the game module
            if self.name == "Tetris Math":
                # Entry point
                from games.TetrisMath.main import main as tetris_main
                tetris_main()
                return True
            # Placeholder
            print(f"{self.name} is a placeholder.")
            return False
        except Exception as e:
            print(f"Error launching game {self.name}: {e}")
            return False

def get_high_scores(game_name):
    score_file = f"scores/{game_name.lower().replace(' ', '_')}_scores.json"
    if not os.path.exists(score_file):
        return []
    
    try:
        with open(score_file, 'r') as f:
            scores = json.load(f)
        return scores
    except Exception:
        return []

def show_high_scores_menu(games):
    running = True
    game_buttons = []
    
    for i, game in enumerate(games):
        # Arrange in a vertical list
        y = 200 + i * 80
        game_buttons.append((Button(SCREEN_WIDTH//2 - 200, y, 400, 60, game.name, font_size=BODY_FONT.get_height()), game))
    
    back_button = Button(SCREEN_WIDTH//2 - 150, 900, 300, 60, "Back to Menu", color=ACCENT_COLOR, hover_color=PRIMARY_COLOR)
    
    while running:
        screen.fill(BG_COLOR)
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = False
        
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                mouse_click = True
        
        # Draw title
        title_text = TITLE_FONT.render("High Scores", True, TEXT_COLOR)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 100))
        screen.blit(title_text, title_rect)
        
        # Draw instructions
        instr_text = SUBTITLE_FONT.render("Select a game to view scores", True, TEXT_COLOR)
        instr_rect = instr_text.get_rect(center=(SCREEN_WIDTH//2, 160))
        screen.blit(instr_text, instr_rect)
        
        # Draw and update game buttons
        for button, game in game_buttons:
            button.update(mouse_pos)
            button.draw(screen)
            if button.is_clicked(mouse_pos, mouse_click):
                show_game_high_scores(game)
        
        # Back button
        back_button.update(mouse_pos)
        back_button.draw(screen)
        if back_button.is_clicked(mouse_pos, mouse_click):
            running = False
            
        pygame.display.flip()
        clock.tick(FPS)

def show_game_high_scores(game):
    scores = get_high_scores(game.name)
    running = True
    back_button = Button(SCREEN_WIDTH//2 - 150, 900, 300, 60, "Back to Scores Menu", color=ACCENT_COLOR, hover_color=PRIMARY_COLOR)
    
    while running:
        screen.fill(BG_COLOR)
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = False
        
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                mouse_click = True
        
        # Draw title
        title_text = TITLE_FONT.render(f"{game.name} High Scores", True, TEXT_COLOR)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 100))
        screen.blit(title_text, title_rect)
        
        # Draw scores
        if not scores:
            no_scores = BODY_FONT.render("No scores yet!", True, TEXT_COLOR)
            no_scores_rect = no_scores.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            screen.blit(no_scores, no_scores_rect)
        else:
            # Sort scores by value, highest first
            sorted_scores = sorted(scores, key=lambda x: x["score"], reverse=True)
            for i, score in enumerate(sorted_scores[:10]):  # Show top 10
                # For Tetris Math, show level instead of difficulty if missing
                difficulty = score.get('difficulty')
                if difficulty is None:
                    # Try to use 'level' or fallback to 'lines_cleared'
                    if 'level' in score:
                        difficulty = f"Level {score['level']}"
                    elif 'lines_cleared' in score:
                        difficulty = f"Lines {score['lines_cleared']}"
                    else:
                        difficulty = "N/A"
                score_text = SCORE_FONT.render(f"{i+1}. {score['name']}: {score['score']} (Difficulty: {difficulty})", True, TEXT_COLOR)
                screen.blit(score_text, (SCREEN_WIDTH//2 - 250, 180 + 50*i))
        
        # Back button
        back_button.update(mouse_pos)
        back_button.draw(screen)
        if back_button.is_clicked(mouse_pos, mouse_click):
            running = False
            
        pygame.display.flip()
        clock.tick(FPS)

def main():
    # Define the games
    games = [
        Game("Word Pop", "Click balloons with correctly spelled words", "word_pop"),
        Game("Math Beats", "Solve math problems coordinated with music rhythm", "math_beats"),
        Game("Spell Quest", "Word puzzle game with masked letters", "spell_quest"),
        Game("Sequence Game", "Identify missing numbers in sequences", "sequence_game"),
        Game("Typing Game", "Type falling words before they hit the ground", "typing_game"),
        Game("Tetris Math", "Combine Tetris with math problems", "TetrisMath.tetrismath", class_name="TetrisGame")
    ]
    
    # Create buttons for each game
    buttons = []
    num_cols = 2
    # num_rows = (len(games) + 1) // 2  # Unused, remove to clean up
    button_width = 300
    button_height = 120
    h_gap = 80
    v_gap = 80
    total_width = num_cols * button_width + (num_cols - 1) * h_gap
    start_x = (SCREEN_WIDTH - total_width) // 2
    for i, game in enumerate(games):
        row = i // num_cols
        col = i % num_cols
        x = start_x + col * (button_width + h_gap)
        y = 200 + row * (button_height + v_gap)
        buttons.append((Button(x, y, button_width, button_height, game.name, font_size=40), game))
    
    # Create a single high scores button
    high_scores_button = Button(SCREEN_WIDTH//2 - 150, 850, 300, 60, "High Scores", color=ACCENT_COLOR, hover_color=PRIMARY_COLOR)
    exit_button = Button(SCREEN_WIDTH//2 - 150, 930, 300, 60, "Exit", color=WARNING_COLOR, hover_color=SECONDARY_COLOR)
    
    # Main game loop
    running = True
    while running:
        screen.fill(BG_COLOR)
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = False
        
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            if event.type == MOUSEBUTTONDOWN:
                mouse_click = True
        
        # Draw title
        title_text = TITLE_FONT.render(TITLE, True, TEXT_COLOR)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 50))
        screen.blit(title_text, title_rect)
        
        # Draw and update game buttons
        for button, game in buttons:
            button.update(mouse_pos)
            button.draw(screen)
            if button.is_clicked(mouse_pos, mouse_click):
                game.launch()
        
        # Draw and update the single high scores button
        high_scores_button.update(mouse_pos)
        high_scores_button.draw(screen)
        if high_scores_button.is_clicked(mouse_pos, mouse_click):
            show_high_scores_menu(games)
        
        # Draw and update exit button
        exit_button.update(mouse_pos)
        exit_button.draw(screen)
        if exit_button.is_clicked(mouse_pos, mouse_click):
            running = False
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()