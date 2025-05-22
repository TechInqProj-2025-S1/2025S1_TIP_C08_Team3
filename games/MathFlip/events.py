 # Event logic
class MathFlipEvents:
    def __init__(self, game):
        self.game = game

    # Event handlers
    def handle_menu_click(self, mouse_pos, buttons):
        for i, button in enumerate(buttons):
            if button.collidepoint(mouse_pos):
                if i == 0:
                    self.game.state = "difficulty"
                elif i == 1:
                    self.game.state = "exit_to_launcher"
