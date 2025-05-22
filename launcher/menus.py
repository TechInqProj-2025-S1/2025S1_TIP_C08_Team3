"""Menus for launcher UI"""
import sys
import pygame
from .constants import (
    BG_COLOR, TEXT_COLOR, ACCENT_COLOR, PRIMARY_COLOR
)
from .button import Button
from .score import get_high_scores

 # Needs global screen/clock from main

def show_high_scores_menu(games, screen, clock, fonts):
    # Show high scores menu
    # pylint: disable=too-many-locals
    title_font, subtitle_font, body_font, _score_font = fonts
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
        game_buttons.append((
            Button(
                real_screen_width // 2 - button_width // 2, y, button_width, button_height,
                game.name, font_size=body_font.get_height(), font=body_font
            ),
            game
        ))
    back_button = Button(
        real_screen_width // 2 - 150, start_y + total_height + 40, 300, 60, "Back to Menu",
        color=ACCENT_COLOR, hover_color=PRIMARY_COLOR, font=body_font
    )
    while running:
        screen.fill(BG_COLOR)
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = False
        for event in pygame.event.get():
            # pylint: disable=no-member
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_click = True
        title_text = title_font.render("High Scores", True, TEXT_COLOR)
        title_rect = title_text.get_rect(center=(real_screen_width // 2, 100))
        screen.blit(title_text, title_rect)
        instr_text = subtitle_font.render("Select a game to view scores", True, TEXT_COLOR)
        instr_rect = instr_text.get_rect(center=(real_screen_width // 2, 160))
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
    # Show high scores for a game
    # pylint: disable=too-many-locals
    title_font, _subtitle_font, body_font, score_font = fonts
    from .score import (
        get_high_scores,
        get_spell_quest_leaderboard,
        get_sequence_game_high_score,
        get_typing_game_leaderboard,
        get_word_pop_high_score
    )
    # Select the appropriate high score/leaderboard reader
    if game.name == "Spell Quest":
        leaderboard = get_spell_quest_leaderboard()
        # Format: list of dicts with 'name' and 'score'
        scores = [
            {"name": entry.get("name", "Unknown"), "score": entry.get("score", 0)}
            for entry in leaderboard if isinstance(entry, dict)
        ]
    elif game.name == "Sequence Game":
        high_score = get_sequence_game_high_score()
        scores = [{"name": "Best Player", "score": high_score}]
    elif game.name == "Typing Game":
        leaderboard = get_typing_game_leaderboard()
        scores = [
            {"name": entry.get("name", "Unknown"), "score": entry.get("score", 0), "difficulty": entry.get("difficulty", "N/A")}
            for entry in leaderboard if isinstance(entry, dict)
        ]
    elif game.name == "Word Pop":
        name, score = get_word_pop_high_score()
        if name is not None:
            scores = [{"name": name, "score": score}]
        else:
            scores = []
    else:
        scores = get_high_scores(game.name)
        # Defensive: filter out entries without a valid 'score' key
        scores = [s for s in scores if isinstance(s, dict) and 'score' in s]
    running = True
    real_screen_width, real_screen_height = screen.get_width(), screen.get_height()
    back_button = Button(
        real_screen_width // 2 - 150, real_screen_height - 120, 300, 60,
        "Back to Scores Menu", color=ACCENT_COLOR, hover_color=PRIMARY_COLOR, font=body_font
    )
    while running:
        screen.fill(BG_COLOR)
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = False
        for event in pygame.event.get():
            # pylint: disable=no-member
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_click = True
        title_text = title_font.render(f"{game.name} High Scores", True, TEXT_COLOR)
        title_rect = title_text.get_rect(center=(real_screen_width // 2, 100))
        screen.blit(title_text, title_rect)
        if not scores:
            no_scores = body_font.render("No scores yet!", True, TEXT_COLOR)
            no_scores_rect = no_scores.get_rect(center=(real_screen_width // 2, real_screen_height // 2))
            screen.blit(no_scores, no_scores_rect)
        else:
            # Sort and display scores appropriately for each game
            if game.name == "Sequence Game":
                # Only one high score
                score = scores[0]
                score_text = score_font.render(f"High Score: {score['score']}", True, TEXT_COLOR)
                screen.blit(score_text, (real_screen_width // 2 - 100, 200))
            elif game.name == "Word Pop":
                score = scores[0]
                score_text = score_font.render(f"{score['name']}: {score['score']}", True, TEXT_COLOR)
                screen.blit(score_text, (real_screen_width // 2 - 100, 200))
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
                            difficulty = None
                    name = score.get('name', 'Unknown')
                    score_val = score.get('score', 0)
                    # Only show difficulty if present
                    if difficulty:
                        score_line = f"{i+1}. {name}: {score_val} (Difficulty: {difficulty})"
                    else:
                        score_line = f"{i+1}. {name}: {score_val}"
                    score_text = score_font.render(score_line, True, TEXT_COLOR)
                    screen.blit(score_text, (real_screen_width // 2 - 250, 180 + 50 * i))
        back_button.update(mouse_pos)
        back_button.draw(screen)
        if back_button.is_clicked(mouse_pos, mouse_click):
            running = False
        pygame.display.flip()
        clock.tick(60)
