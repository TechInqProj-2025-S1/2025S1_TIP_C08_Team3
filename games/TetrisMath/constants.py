import pygame

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 700
GRID_SIZE = 26
GRID_WIDTH = 10
GRID_HEIGHT = 20
SIDEBAR_WIDTH = 240

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
PURPLE = (155, 89, 182)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

PRIMARY_COLOR = (52, 152, 219)
SECONDARY_COLOR = (41, 128, 185)
ACCENT_COLOR = (46, 204, 113)
WARNING_COLOR = (231, 76, 60)
BG_COLOR = (236, 240, 241)
TEXT_COLOR = (44, 62, 80)
BLOCK_COLORS = [PRIMARY_COLOR, SECONDARY_COLOR, ACCENT_COLOR, WARNING_COLOR, (241, 196, 15), PURPLE, ORANGE]


# Font getter to ensure pygame is initialized before font creation
_fonts_cache = None
def get_fonts():
    global _fonts_cache
    if _fonts_cache is None:
        # Defensive: ensure font module is initialized
        if not pygame.font.get_init():
            pygame.font.init()
        _fonts_cache = {
            'TITLE_FONT': pygame.font.SysFont(['San Francisco', 'Helvetica Neue', 'Arial', 'sans-serif'], 60, bold=True),
            'BODY_FONT': pygame.font.SysFont(['San Francisco', 'Helvetica Neue', 'Arial', 'sans-serif'], 32),
            'SCORE_FONT': pygame.font.SysFont(['San Francisco', 'Helvetica Neue', 'Arial', 'sans-serif'], 28),
        }
    return _fonts_cache

# For backward compatibility in tests
TITLE_FONT = None

DIFFICULTY_COLORS = {
    'basic': GREEN,
    'master': PURPLE
}
