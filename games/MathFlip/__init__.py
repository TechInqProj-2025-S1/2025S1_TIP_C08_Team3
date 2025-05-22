# Math Flip Game main entry point for launcher integration
from .voltorb import MathFlipGame
def main(*args, **kwargs):
    import pygame
    screen = pygame.display.get_surface()
    game = MathFlipGame(screen=screen)
    game.run()
