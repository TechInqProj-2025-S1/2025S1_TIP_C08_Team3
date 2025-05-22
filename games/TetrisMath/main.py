from .ui import TetrisMathUI


def main(screen_width=None, screen_height=None, fullscreen=True, screen=None):
    # Try to reuse the current display surface if possible
    if screen is None:
        import pygame
        screen = pygame.display.get_surface()
    ui = TetrisMathUI(screen_width=screen_width, screen_height=screen_height, fullscreen=fullscreen, screen=screen)
    ui.run()

if __name__ == "__main__":
    main()
