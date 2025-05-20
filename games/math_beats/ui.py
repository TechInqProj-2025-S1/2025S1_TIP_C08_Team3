
import pygame
from .constants import (
    BG_COLOR, PRIMARY_COLOR, BUTTON_COLOR, BUTTON_HOVER_COLOR, BUTTON_TEXT_COLOR, WHITE, BLACK, TEXT_COLOR, SCREEN_WIDTH, SCREEN_HEIGHT, LANE_COUNT
)

class Button:
    def __init__(self, rect, text, color, hover_color, font, text_color=BUTTON_TEXT_COLOR):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.font = font
        self.text_color = text_color
        self.hovered = False
    def draw(self, surface):
        pygame.draw.rect(surface, self.hover_color if self.hovered else self.color, self.rect, border_radius=10)
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)
    def is_clicked(self, mouse_pos, mouse_click):
        return self.rect.collidepoint(mouse_pos) and mouse_click

class MathBeatsUI:
    def __init__(self, screen, fonts):
        self.screen = screen
        self.fonts = fonts
        self.lane_rects = self._make_lanes()
        self.hit_line_y = int(SCREEN_HEIGHT * 0.8)
    def _make_lanes(self):
        lane_w = SCREEN_WIDTH // (LANE_COUNT + 1)
        rects = []
        for i in range(LANE_COUNT):
            x = lane_w * (i + 1) - lane_w // 2 - 60
            rects.append(pygame.Rect(x, 0, 120, SCREEN_HEIGHT))
        return rects
    def draw_bg(self):
        self.screen.fill(WHITE)
    def draw_lanes(self):
        for rect in self.lane_rects:
            pygame.draw.rect(self.screen, BG_COLOR, rect, border_radius=16)
        pygame.draw.line(self.screen, PRIMARY_COLOR, (0, self.hit_line_y), (SCREEN_WIDTH, self.hit_line_y), 6)
    def draw_problem(self, problem):
        text = f"{problem['a']} {problem['op']} {problem['b']} = ?"
        surf = self.fonts['TITLE_FONT'].render(text, True, TEXT_COLOR)
        self.screen.blit(surf, (SCREEN_WIDTH//2 - surf.get_width()//2, 40))
    def draw_choices(self, drops):
        for drop in drops:
            lane = drop['lane']
            y = drop['y']
            val = drop['value']
            color = PRIMARY_COLOR if not drop.get('hit') else (46, 204, 113) if drop['correct'] else (231, 76, 60)
            surf = self.fonts['BODY_FONT'].render(str(val), True, WHITE)
            rect = self.lane_rects[lane].copy()
            rect.y = y
            rect.height = 60
            pygame.draw.rect(self.screen, color, rect, border_radius=12)
            self.screen.blit(surf, (rect.centerx - surf.get_width()//2, rect.centery - surf.get_height()//2))
    def draw_hud(self, score, lives):
        score_surf = self.fonts['SCORE_FONT'].render(f"Score: {score}", True, TEXT_COLOR)
        lives_surf = self.fonts['SCORE_FONT'].render(f"Lives: {lives}", True, TEXT_COLOR)
        self.screen.blit(score_surf, (30, 20))
        self.screen.blit(lives_surf, (SCREEN_WIDTH - lives_surf.get_width() - 30, 20))
    def draw_feedback(self, correct):
        msg = "Correct!" if correct else "Wrong!"
        color = (46, 204, 113) if correct else (231, 76, 60)
        surf = self.fonts['BODY_FONT'].render(msg, True, color)
        self.screen.blit(surf, (SCREEN_WIDTH//2 - surf.get_width()//2, self.hit_line_y + 30))
    def draw_game_over(self, score):
        surf = self.fonts['TITLE_FONT'].render("Game Over", True, WARNING_COLOR)
        self.screen.blit(surf, (SCREEN_WIDTH//2 - surf.get_width()//2, 200))
        score_surf = self.fonts['BODY_FONT'].render(f"Final Score: {score}", True, TEXT_COLOR)
        self.screen.blit(score_surf, (SCREEN_WIDTH//2 - score_surf.get_width()//2, 300))
