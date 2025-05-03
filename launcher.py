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
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
PRIMARY_COLOR = (52, 152, 219)  # Blue
SECONDARY_COLOR = (41, 128, 185)  # Darker Blue
ACCENT_COLOR = (46, 204, 113)  # Green
WARNING_COLOR = (231, 76, 60)  # Red
BG_COLOR = (236, 240, 241)  # Light Gray
TEXT_COLOR = (44, 62, 80)  # Dark Gray
BUTTON_COLOR = (102, 187, 239)  # #66bbef
BUTTON_HOVER_COLOR = (82, 167, 219)  # Slightly darker for hover
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
    high_scores_button = Button(SCREEN_WIDTH//2 - 310, 850, 300, 60, "High Scores", color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR, text_color=BUTTON_TEXT_COLOR)
    settings_button = Button(SCREEN_WIDTH//2 + 10, 850, 300, 60, "Settings", color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR, text_color=BUTTON_TEXT_COLOR)
    exit_button = Button(SCREEN_WIDTH//2 - 150, 930, 300, 60, "Exit", color=WARNING_COLOR, hover_color=SECONDARY_COLOR)
    
    # Ensure config.json exists
    config_path = os.path.join(os.getcwd(), "config.json")
    if not os.path.exists(config_path):
        with open(config_path, "w") as f:
            json.dump({"launcher": {}, "games": {}}, f, indent=2)

    def show_settings_menu():
        running = True
        # Load config
        with open(config_path, "r") as f:
            config = json.load(f)
        font = BODY_FONT
        # Multiplayer Tetris Math settings
        tetris_multiplayer = config.get("games", {}).get("tetris_math_multiplayer", {})
        host_ip = tetris_multiplayer.get("host_ip", "127.0.0.1")
        host_port = str(tetris_multiplayer.get("host_port", "5000"))
        input_active = None
        back_button = Button(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT - 120, 300, 60, "Back", color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR, text_color=BUTTON_TEXT_COLOR)
        ip_box = pygame.Rect(SCREEN_WIDTH//2 - 180, 350, 200, 50)
        port_box = pygame.Rect(SCREEN_WIDTH//2 + 40, 350, 120, 50)
        while running:
            screen.fill(BG_COLOR)
            title = TITLE_FONT.render("Settings", True, TEXT_COLOR)
            screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 60))
            y = 180
            # General launcher settings
            launcher_label = font.render("Launcher Settings", True, PRIMARY_COLOR)
            screen.blit(launcher_label, (SCREEN_WIDTH//2 - launcher_label.get_width()//2, y))
            y += 50
            # Placeholder for launcher settings
            launcher_setting = font.render("(No settings yet)", True, TEXT_COLOR)
            screen.blit(launcher_setting, (SCREEN_WIDTH//2 - launcher_setting.get_width()//2, y))
            y += 80
            # Tetris Math Multiplayer settings
            tetris_label = font.render("Tetris Math Multiplayer", True, ACCENT_COLOR)
            screen.blit(tetris_label, (SCREEN_WIDTH//2 - tetris_label.get_width()//2, y))
            y += 40
            ip_label = font.render("Host IP:", True, TEXT_COLOR)
            port_label = font.render("Host Port:", True, TEXT_COLOR)
            # Draw IP and Port labels and boxes with more vertical spacing to avoid overlap
            screen.blit(ip_label, (SCREEN_WIDTH//2 - 220, 360))
            screen.blit(port_label, (SCREEN_WIDTH//2 + 10, 360))
            pygame.draw.rect(screen, WHITE, ip_box, 2, border_radius=8)
            pygame.draw.rect(screen, WHITE, port_box, 2, border_radius=8)
            ip_surf = font.render(host_ip, True, BLACK)
            port_surf = font.render(host_port, True, BLACK)
            screen.blit(ip_surf, (ip_box.x + 10, ip_box.y + 10))
            screen.blit(port_surf, (port_box.x + 10, port_box.y + 10))
            # Instructions
            instr = SCORE_FONT.render("Set IP/Port for LAN play. Host: share your IP/port. Join: enter host's IP/port.", True, TEXT_COLOR)
            screen.blit(instr, (SCREEN_WIDTH//2 - instr.get_width()//2, 430))
            # Per-game settings placeholders
            y = 530  # Increased from 500 to 530 for more space
            for game in games:
                if game.name != "Tetris Math":
                    game_label = font.render(f"{game.name} Settings", True, ACCENT_COLOR)
                    screen.blit(game_label, (SCREEN_WIDTH//2 - game_label.get_width()//2, y))
                    y += 40
                    game_setting = font.render("(No settings yet)", True, TEXT_COLOR)
                    screen.blit(game_setting, (SCREEN_WIDTH//2 - game_setting.get_width()//2, y))
                    y += 60
            back_button.update(pygame.mouse.get_pos())
            back_button.draw(screen)
            mouse_click = False
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == MOUSEBUTTONDOWN:
                    mouse_click = True
                    if ip_box.collidepoint(event.pos):
                        input_active = 'ip'
                    elif port_box.collidepoint(event.pos):
                        input_active = 'port'
                    else:
                        input_active = None
                if event.type == pygame.KEYDOWN and input_active:
                    if input_active == 'ip':
                        if event.key == pygame.K_BACKSPACE:
                            host_ip = host_ip[:-1]
                        elif len(host_ip) < 15 and (event.unicode.isdigit() or event.unicode == '.' or event.unicode == ':'):
                            host_ip += event.unicode
                    elif input_active == 'port':
                        if event.key == pygame.K_BACKSPACE:
                            host_port = host_port[:-1]
                        elif len(host_port) < 5 and event.unicode.isdigit():
                            host_port += event.unicode
            if back_button.is_clicked(pygame.mouse.get_pos(), mouse_click):
                # Save settings
                config.setdefault("games", {})["tetris_math_multiplayer"] = {"host_ip": host_ip, "host_port": int(host_port) if host_port.isdigit() else 5000}
                with open(config_path, "w") as f:
                    json.dump(config, f, indent=2)
                running = False
            pygame.display.flip()
            clock.tick(FPS)

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
        # Draw and update the high scores button
        high_scores_button.update(mouse_pos)
        high_scores_button.draw(screen)
        if high_scores_button.is_clicked(mouse_pos, mouse_click):
            show_high_scores_menu(games)
        # Draw and update the settings button
        settings_button.update(mouse_pos)
        settings_button.draw(screen)
        if settings_button.is_clicked(mouse_pos, mouse_click):
            show_settings_menu()
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