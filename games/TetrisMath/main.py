from .ui import TetrisMathUI


def main(screen_width=None, screen_height=None, fullscreen=True):
    ui = TetrisMathUI(screen_width=screen_width, screen_height=screen_height, fullscreen=fullscreen)
    ui.run()

if __name__ == "__main__":
    main()
