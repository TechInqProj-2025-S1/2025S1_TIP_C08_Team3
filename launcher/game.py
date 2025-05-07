class Game:
    def __init__(self, name, description, module_name, class_name=None):
        self.name = name
        self.description = description
        self.module_name = module_name
        self.class_name = class_name
        
    def launch(self, screen_width=None, screen_height=None, fullscreen=True):
        try:
            # Dynamic import of the game module
            if self.name == "Tetris Math":
                # Entry point
                from games.TetrisMath.main import main as tetris_main
                tetris_main(screen_width=screen_width, screen_height=screen_height, fullscreen=fullscreen)
                return True
            # Placeholder
            print(f"{self.name} is a placeholder.")
            return False
        except Exception as e:
            print(f"Error launching game {self.name}: {e}")
            return False
