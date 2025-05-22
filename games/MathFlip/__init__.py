 # Entry for launcher
from .mathflip_game import MathFlipGame

def main(*args, **kwargs):
    import pygame
    screen = pygame.display.get_surface()
    game = MathFlipGame(screen=screen)
    game.run()
