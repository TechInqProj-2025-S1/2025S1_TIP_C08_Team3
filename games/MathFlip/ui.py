# UI logic
import pygame
from .constants import *
from .fonts import FONT_LARGE, FONT_MEDIUM, FONT_SMALL

class MathFlipUI:
    def __init__(self, game):
        self.game = game

    def draw_menu(self):
        surf = self.game.DISPLAYSURF
        surf.fill(BG_COLOR)
        title = FONT_LARGE.render("Math Flip Game", True, PRIMARY_COLOR)
        title_y = 120
        surf.blit(title, (self.game.WINDOW_WIDTH//2 - title.get_width()//2, title_y))
        button_width = 240
        button_height = 56
        spacing = 32
        center_x = self.game.WINDOW_WIDTH // 2
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

    # More draw methods can be added.
