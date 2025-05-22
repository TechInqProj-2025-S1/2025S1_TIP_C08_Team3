"""
Main launcher for the game application.
"""
# pylint: disable=line-too-long, too-many-locals, too-many-branches, too-many-statements, superfluous-parens, no-member
import sys
import os
import json
import pygame

from launcher.constants import (
    TITLE, FPS,
    BG_COLOR, TEXT_COLOR, BUTTON_COLOR, BUTTON_HOVER_COLOR, BUTTON_TEXT_COLOR,
    WARNING_COLOR, SECONDARY_WARNING_COLOR
)
from launcher.button import Button
from launcher.game import Game
# get_high_scores is only used in menus, not here
from launcher.menus import show_high_scores_menu
from launcher.settings_menu import show_settings_menu



# Initialize pygame
# pylint: disable=no-member
pygame.init()  # pylint: disable=no-member
pygame.mixer.init()  # For sound effects

# Fonts (must be initialized after pygame.init)
TITLE_FONT = pygame.font.SysFont('arial', 60, bold=True)
SUBTITLE_FONT = pygame.font.SysFont('arial', 36, bold=True)
BODY_FONT = pygame.font.SysFont('arial', 32)
SCORE_FONT = pygame.font.SysFont('arial', 28)



# Create the screen in FULLSCREEN BORDERLESS mode and get actual monitor size
# pylint: disable=no-member

info = pygame.display.Info()  # pylint: disable=no-member
real_screen_width = info.current_w
real_screen_height = info.current_h
screen = pygame.display.set_mode(
    (real_screen_width, real_screen_height),
    pygame.NOFRAME  # pylint: disable=no-member
)
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()

# Ensure the scores directory exists
if not os.path.exists("scores"):
    os.makedirs("scores")


def main():
    """Main function for the game launcher. Sets up UI, handles events, and launches games."""
    fonts = (TITLE_FONT, SUBTITLE_FONT, BODY_FONT, SCORE_FONT)
    # Save display settings to config for games to read
    config_path = os.path.join(os.getcwd(), "config.json")
    if not os.path.exists(config_path):
        config = {"launcher": {}, "games": {}}
    else:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    config["launcher"]["display"] = {
        "width": real_screen_width,
        "height": real_screen_height,
        "borderless": True
    }
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

    # Define the games
    games = [
        Game("Word Pop", "Click balloons with correctly spelled words", "word_pop"),
        Game("Math Flip", "Match math questions to answers in a grid", "MathFlip.voltorb"),
        Game("Spell Quest", "Word puzzle game with masked letters", "spell_quest"),
        Game("Sequence Game", "Identify missing numbers in sequences", "sequence_game"),
        Game("Typing Game", "Type falling words before they hit the ground", "typing_game"),
        Game(
            "Tetris Math", "Combine Tetris with math problems",
            "TetrisMath.tetrismath", class_name="TetrisGame"
        )
    ]

    # Dynamic, Responsive base on current Screen Resolution
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

    # Game Button
    buttons = []
    for i, game in enumerate(games):
        row = i // num_cols
        col = i % num_cols
        x = start_x + col * (button_width + h_gap)
        y = start_y + row * (button_height + v_gap)
        buttons.append((Button(x, y, button_width, button_height, game.name, font_size=40, font=BODY_FONT), game))

    # Menu buttons
    menu_y = start_y + total_height + 40
    menu_gap = 40
    menu_button_width = int(0.4 * total_width // 2)
    menu_button_width = max(menu_button_width, 180)
    menu_button_height = 60
    # Button group centered
    # pylint: disable=line-too-long
    total_menu_width = menu_button_width * 2 + menu_gap  # no parens, avoid C0325
    menu_start_x = real_screen_width // 2 - total_menu_width // 2
    high_scores_button = Button(
        menu_start_x, menu_y, menu_button_width, menu_button_height, "High Scores",
        color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR,
        text_color=BUTTON_TEXT_COLOR, font=BODY_FONT
    )
    settings_button = Button(
        menu_start_x + menu_button_width + menu_gap, menu_y,
        menu_button_width, menu_button_height, "Settings",
        color=BUTTON_COLOR, hover_color=BUTTON_HOVER_COLOR,
        text_color=BUTTON_TEXT_COLOR, font=BODY_FONT
    )
    exit_button = Button(
        real_screen_width // 2 - 150, menu_y + menu_button_height + 30,
        300, 60, "Exit",
        color=WARNING_COLOR, hover_color=SECONDARY_WARNING_COLOR, font=BODY_FONT
    )

    # Ensure config.json exists
    config_path = os.path.join(os.getcwd(), "config.json")
    if not os.path.exists(config_path):
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump({"launcher": {}, "games": {}}, f, indent=2)

    # pylint: disable=too-many-locals, too-many-branches, too-many-statements, line-too-long, no-member, superfluous-parens

    # Main game loop
    running = True
    while running:
        screen.fill(BG_COLOR)
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # pylint: disable=no-member
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:  # pylint: disable=no-member
                mouse_click = True
        # Tittle
        title_text = TITLE_FONT.render(TITLE, True, TEXT_COLOR)
        title_rect = title_text.get_rect(center=(real_screen_width // 2, start_y // 2))
        screen.blit(title_text, title_rect)
        # Draw and update game buttons
        for button, game in buttons:
            button.update(mouse_pos)
            button.draw(screen)
            if button.is_clicked(mouse_pos, mouse_click):
                # Pass launcher display settings to the game
                if game.name == "Tetris Math":
                    game.launch(
                        screen_width=real_screen_width,
                        screen_height=real_screen_height,
                        fullscreen=True
                    )
                else:
                    game.launch()
        # High scores button
        high_scores_button.update(mouse_pos)
        high_scores_button.draw(screen)
        if high_scores_button.is_clicked(mouse_pos, mouse_click):
            show_high_scores_menu(games, screen, clock, fonts)

        # Settings button
        settings_button.update(mouse_pos)
        settings_button.draw(screen)
        if settings_button.is_clicked(mouse_pos, mouse_click):
            show_settings_menu(games, screen, clock, config_path, fonts)

        # Exit button
        exit_button.update(mouse_pos)
        exit_button.draw(screen)
        if exit_button.is_clicked(mouse_pos, mouse_click):
            running = False

        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()  # pylint: disable=no-member
    sys.exit()


# Entry point
if __name__ == "__main__":
    main()
