# Math Flip Game main entry point for launcher integration
from .voltorb import MathFlipGame
def main(*args, **kwargs):
    game = MathFlipGame()
    game.run()
