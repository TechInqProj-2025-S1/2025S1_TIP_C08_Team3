"""
Main launcher for the game application.
"""
import pygame
from pygame.locals import QUIT, MOUSEBUTTONDOWN
import sys
import os
import json
from launcher.constants import (
    TITLE, FPS,
    BG_COLOR, TEXT_COLOR, BUTTON_COLOR, BUTTON_HOVER_COLOR, BUTTON_TEXT_COLOR,
    WARNING_COLOR, SECONDARY_COLOR
)
from launcher.button import Button
from launcher.game import Game
## get_high_scores is only used in menus, not here
from launcher.menus import show_high_scores_menu
from launcher.settings_menu import show_settings_menu


# Initialize pygame
pygame.init()
pygame.mixer.init()  # For sound effects

# Fonts (must be initialized after pygame.init)
TITLE_FONT = pygame.font.SysFont('arial', 60, bold=True)
SUBTITLE_FONT = pygame.font.SysFont('arial', 36, bold=True)
BODY_FONT = pygame.font.SysFont('arial', 32)
SCORE_FONT = pygame.font.SysFont('arial', 28)


# Create the screen in FULLSCREEN BORDERLESS mode and get actual monitor size
info = pygame.display.Info()
real_screen_width, real_screen_height = info.current_w, info.current_h
screen = pygame.display.set_mode((real_screen_width, real_screen_height), pygame.NOFRAME)
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()

# Ensure the scores directory exists
if not os.path.exists("scores"):
    os.makedirs("scores")


def main():
    # Fonts (must be initialized after pygame.init)
    TITLE_FONT = pygame.font.SysFont('arial', 60, bold=True)
    SUBTITLE_FONT = pygame.font.SysFont('arial', 36, bold=True)
    BODY_FONT = pygame.font.SysFont('arial', 32)
    SCORE_FONT = pygame.font.SysFont('arial', 28)
    fonts = (TITLE_FONT, SUBTITLE_FONT, BODY_FONT, SCORE_FONT)
    # Save display settings to config for games to read
    config_path = os.path.join(os.getcwd(), "config.json")
    if not os.path.exists(config_path):
        config = {"launcher": {}, "games": {}}
    else:
        with open(config_path, "r") as f:
            config = json.load(f)
    config["launcher"]["display"] = {
        "width": real_screen_width,
        "height": real_screen_height,
        "borderless": True
    }
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)

    # Define the games
    games = [
        Game("Word Pop", "Click balloons with correctly spelled words", "word_pop"),
        Game("Math Beats", "Solve math problems coordinated with music rhythm", "math_beats"),
        Game("Spell Quest", "Word puzzle game with masked letters", "spell_quest"),
        Game("Sequence Game", "Identify missing numbers in sequences", "sequence_game"),
        Game("Typing Game", "Type falling words before they hit the ground", "typing_game"),
        Game("Tetris Math", "Combine Tetris with math problems", "TetrisMath.tetrismath", class_name="TetrisGame")
    ]
    
    # Responsive layout: calculate available area and center all UI vertically and horizontally
    num_cols = 2
    num_rows = 3
    button_width = 300
    button_height = 120
    h_gap = 80
    v_gap = 60
    # Calculate total width and height of the button grid
    total_width = num_cols * button_width + (num_cols - 1) * h_gap
    total_height = num_rows * button_height + (num_rows - 1) * v_gap
    # Center grid
    start_x = (real_screen_width - total_width) // 2
    start_y = 160
    # If screen is too small, scale down buttons and gaps
    min_margin = 40
    if real_screen_width < total_width + min_margin * 2 or real_screen_height < total_height + 350:
        scale_x = (real_screen_width - min_margin * 2) / total_width
        scale_y = (real_screen_height - 350 - min_margin * 2) / total_height
        scale = min(scale_x, scale_y, 1.0)
        button_width = int(button_width * scale)
        button_height = int(button_height * scale)
        h_gap = int(h_gap * scale)
        v_gap = int(v_gap * scale)
        total_width = num_cols * button_width + (num_cols - 1) * h_gap
        total_height = num_rows * button_height + (num_rows - 1) * v_gap
        start_x = (real_screen_width - total_width) // 2
        start_y = max(100, (real_screen_height - total_height) // 2 - 60)

    # Create buttons for each game
    buttons = []
    for i, game in enumerate(games):
        row = i // num_cols
        col = i % num_cols
        x = start_x + col * (button_width + h_gap)
        y = start_y + row * (button_height + v_gap)
        buttons.append((Button(x, y, button_width, button_height, game.name, font_size=40, font=BODY_FONT), game))

    # Menu buttons (centered below game grid)
    menu_y = start_y + total_height + 40
    menu_gap = 40
    menu_button_width = int(0.4 * total_width // 2)
    menu_button_width = max(menu_button_width, 180)
    menu_button_height = 60
    # Center both buttons as a group
    total_menu_width = menu_button_width * 2 + menu_gap
    menu_start_x = real_screen_width // 2 - total_menu_width // 2
    high_scores_button = Button(menu_start_x, menu_y, menu_button_width, menu_button_height, "High Scores", color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR, text_color=BUTTON_TEXT_COLOR, font=BODY_FONT)
    settings_button = Button(menu_start_x + menu_button_width + menu_gap, menu_y, menu_button_width, menu_button_height, "Settings", color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR, text_color=BUTTON_TEXT_COLOR, font=BODY_FONT)
    exit_button = Button(real_screen_width//2 - 150, menu_y + menu_button_height + 30, 300, 60, "Exit", color=WARNING_COLOR, hover_color=SECONDARY_COLOR, font=BODY_FONT)
    
    # Ensure config.json exists
    config_path = os.path.join(os.getcwd(), "config.json")
    if not os.path.exists(config_path):
        with open(config_path, "w") as f:
            json.dump({"launcher": {}, "games": {}}, f, indent=2)



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
        # Draw title (centered at top)
        title_text = TITLE_FONT.render(TITLE, True, TEXT_COLOR)
        title_rect = title_text.get_rect(center=(real_screen_width//2, start_y // 2))
        screen.blit(title_text, title_rect)
        # Draw and update game buttons
        for button, game in buttons:
            button.update(mouse_pos)
            button.draw(screen)
            if button.is_clicked(mouse_pos, mouse_click):
                # Pass launcher display settings to the game
                if game.name == "Tetris Math":
                    game.launch(screen_width=real_screen_width, screen_height=real_screen_height, fullscreen=True)
                else:
                    game.launch()
        # Draw and update the high scores button
        high_scores_button.update(mouse_pos)
        high_scores_button.draw(screen)
        if high_scores_button.is_clicked(mouse_pos, mouse_click):
            show_high_scores_menu(games, screen, clock, fonts)
        # Draw and update the settings button
        settings_button.update(mouse_pos)
        settings_button.draw(screen)
        if settings_button.is_clicked(mouse_pos, mouse_click):
            show_settings_menu(games, screen, clock, config_path, fonts)
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