
import pygame
import os
import random
from games.math_beats.constants import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE
from games.math_beats.ui import MathBeatsUI
from games.math_beats.beats import BeatDetector
from games.math_beats.problems import generate_problem

def get_fonts():
    pygame.font.init()
    return {
        'TITLE_FONT': pygame.font.SysFont('Arial', 56, bold=True),
        'BODY_FONT': pygame.font.SysFont('Arial', 36),
        'SCORE_FONT': pygame.font.SysFont('Arial', 28, bold=True),
    }

def main(screen_width=None, screen_height=None, fullscreen=True):
    pygame.init()
    screen = pygame.display.set_mode((screen_width or SCREEN_WIDTH, screen_height or SCREEN_HEIGHT))
    pygame.display.set_caption("Math Beats")
    fonts = get_fonts()
    ui = MathBeatsUI(screen, fonts)
    clock = pygame.time.Clock()
    running = True
    # --- Loading/analysis state ---
    # For now, use a fixed song in assets
    song_path = os.path.join(os.path.dirname(__file__), '../../assets/sample.mp3')
    if not os.path.exists(song_path):
        screen.fill(WHITE)
        surf = fonts['TITLE_FONT'].render("No song found in assets!", True, (200,0,0))
        screen.blit(surf, (screen.get_width()//2 - surf.get_width()//2, 200))
        pygame.display.flip()
        pygame.time.wait(2000)
        return
    detector = BeatDetector(song_path)
    beats, bpm = detector.analyze()
    # --- Game state ---
    score = 0
    lives = 3
    beat_idx = 0
    drops = []
    problem = generate_problem(bpm)    # Assign choices to random lanes
    lanes = list(range(3))
    random.shuffle(lanes)
    for i, val in enumerate(problem['choices']):
        drops.append({'lane': lanes[i], 'y': -60, 'value': val, 'correct': val == problem['answer'], 'hit': False})
    # Calculate drop speed based on beat intervals
    drop_speed = int((beats[1] - beats[0]) * 1.5) if len(beats) > 1 else 1000
    hit_window = 200
    feedback = None
    feedback_timer = 0
    # --- Main loop ---
    pygame.mixer.music.load(song_path)
    pygame.mixer.music.play()
    while running:
        dt = clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_1, pygame.K_KP1):
                    lane = 0
                elif event.key in (pygame.K_2, pygame.K_KP2):
                    lane = 1
                elif event.key in (pygame.K_3, pygame.K_KP3):
                    lane = 2
                else:
                    lane = None
                if lane is not None:
                    for drop in drops:
                        if drop['lane'] == lane and abs(drop['y'] - ui.hit_line_y) < hit_window:
                            drop['hit'] = True
                            if drop['correct']:
                                score += 1
                                feedback = True
                            else:
                                lives -= 1
                                feedback = False
                            feedback_timer = 30
                            break
        # Move drops
        for drop in drops:
            drop['y'] += drop_speed * dt / 1000
        # Remove drops that passed hit line
        for drop in drops:
            if drop['y'] > ui.hit_line_y + hit_window and not drop['hit']:
                lives -= 1
                drop['hit'] = True
                feedback = False
                feedback_timer = 30
        drops = [d for d in drops if d['y'] < SCREEN_HEIGHT and not (d['hit'] and feedback_timer == 0)]
        # Spawn new drops on next beat
        if beat_idx + 1 < len(beats) and pygame.mixer.music.get_pos() >= beats[beat_idx+1]:
            beat_idx += 1
            if len(drops) == 0 or all(d['hit'] for d in drops):
                problem = generate_problem(bpm)
                lanes = list(range(3))
                random.shuffle(lanes)
                drops = []
                for i, val in enumerate(problem['choices']):
                    drops.append({'lane': lanes[i], 'y': -60, 'value': val, 'correct': val == problem['answer'], 'hit': False})
        # Draw
        ui.draw_bg()
        ui.draw_lanes()
        ui.draw_problem(problem)
        ui.draw_choices(drops)
        ui.draw_hud(score, lives)
        if feedback is not None:
            ui.draw_feedback(feedback)
            feedback_timer -= 1
            if feedback_timer <= 0:
                feedback = None
        if lives <= 0:
            ui.draw_game_over(score)
            pygame.display.flip()
            pygame.time.wait(2000)
            running = False
            break
        pygame.display.flip()
    pygame.quit()
