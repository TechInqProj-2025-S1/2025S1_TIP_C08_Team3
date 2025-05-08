import pygame
import sys
from .constants import (
    BG_COLOR, TEXT_COLOR, ACCENT_COLOR, PRIMARY_COLOR
)
from .button import Button
from .score import get_high_scores

# These functions require the global 'screen' and 'clock' to be set in the main launcher

def show_high_scores_menu(games, screen, clock, fonts):
    TITLE_FONT, SUBTITLE_FONT, BODY_FONT, SCORE_FONT = fonts
    running = True
    game_buttons = []
    # Responsive centering
    real_screen_width, real_screen_height = screen.get_width(), screen.get_height()
    button_width = 400
    button_height = 60
    v_gap = 20
    total_height = len(games) * button_height + (len(games) - 1) * v_gap
    start_y = max(200, (real_screen_height - total_height) // 2)
    for i, game in enumerate(games):
        y = start_y + i * (button_height + v_gap)
        game_buttons.append((Button(real_screen_width//2 - button_width//2, y, button_width, button_height, game.name, font_size=BODY_FONT.get_height(), font=BODY_FONT), game))
    back_button = Button(real_screen_width//2 - 150, start_y + total_height + 40, 300, 60, "Back to Menu", color=ACCENT_COLOR, hover_color=PRIMARY_COLOR, font=BODY_FONT)
    while running:
        screen.fill(BG_COLOR)
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_click = True
        title_text = TITLE_FONT.render("High Scores", True, TEXT_COLOR)
        title_rect = title_text.get_rect(center=(real_screen_width//2, 100))
        screen.blit(title_text, title_rect)
        instr_text = SUBTITLE_FONT.render("Select a game to view scores", True, TEXT_COLOR)
        instr_rect = instr_text.get_rect(center=(real_screen_width//2, 160))
        screen.blit(instr_text, instr_rect)
        for button, game in game_buttons:
            button.update(mouse_pos)
            button.draw(screen)
            if button.is_clicked(mouse_pos, mouse_click):
                show_game_high_scores(game, screen, clock, fonts)
        back_button.update(mouse_pos)
        back_button.draw(screen)
        if back_button.is_clicked(mouse_pos, mouse_click):
            running = False
        pygame.display.flip()
        clock.tick(60)

def show_game_high_scores(game, screen, clock, fonts):
    TITLE_FONT, SUBTITLE_FONT, BODY_FONT, SCORE_FONT = fonts
    scores = get_high_scores(game.name)
    # Defensive: filter out entries without a valid 'score' key
    scores = [s for s in scores if isinstance(s, dict) and 'score' in s]
    running = True
    real_screen_width, real_screen_height = screen.get_width(), screen.get_height()
    back_button = Button(real_screen_width//2 - 150, real_screen_height - 120, 300, 60, "Back to Scores Menu", color=ACCENT_COLOR, hover_color=PRIMARY_COLOR, font=BODY_FONT)
    while running:
        screen.fill(BG_COLOR)
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_click = True
        title_text = TITLE_FONT.render(f"{game.name} High Scores", True, TEXT_COLOR)
        title_rect = title_text.get_rect(center=(real_screen_width//2, 100))
        screen.blit(title_text, title_rect)
        if not scores:
            no_scores = BODY_FONT.render("No scores yet!", True, TEXT_COLOR)
            no_scores_rect = no_scores.get_rect(center=(real_screen_width//2, real_screen_height//2))
            screen.blit(no_scores, no_scores_rect)
        else:
            sorted_scores = sorted(scores, key=lambda x: x.get("score", 0), reverse=True)
            for i, score in enumerate(sorted_scores[:10]):
                difficulty = score.get('difficulty')
                if difficulty is None:
                    if 'level' in score:
                        difficulty = f"Level {score['level']}"
                    elif 'lines_cleared' in score:
                        difficulty = f"Lines {score['lines_cleared']}"
                    else:
                        difficulty = "N/A"
                # Defensive: handle missing name or score keys
                name = score.get('name', 'Unknown')
                score_val = score.get('score', 0)
                score_text = SCORE_FONT.render(f"{i+1}. {name}: {score_val} (Difficulty: {difficulty})", True, TEXT_COLOR)
                screen.blit(score_text, (real_screen_width//2 - 250, 180 + 50*i))
        back_button.update(mouse_pos)
        back_button.draw(screen)
        if back_button.is_clicked(mouse_pos, mouse_click):
            running = False
        pygame.display.flip()
        clock.tick(60)
