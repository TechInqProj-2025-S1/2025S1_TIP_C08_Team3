# Fonts
import pygame

def get_launcher_fonts():
    font_list = ['San Francisco', 'Helvetica Neue', 'Arial', 'sans-serif']
    if not pygame.font.get_init():
        pygame.font.init()
    return {
        'TITLE_FONT': pygame.font.SysFont(font_list, 60, bold=True),
        'BODY_FONT': pygame.font.SysFont(font_list, 32),
        'SCORE_FONT': pygame.font.SysFont(font_list, 28),
    }

_FONTS = get_launcher_fonts()
FONT_LARGE = _FONTS['TITLE_FONT']
FONT_MEDIUM = _FONTS['BODY_FONT']
FONT_SMALL = _FONTS['SCORE_FONT']
