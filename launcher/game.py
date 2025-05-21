"""Game class for handling game launching logic in the Team 3 Launcher."""

class Game:
    """Represents a game entry in the launcher."""
    # pylint: disable=too-few-public-methods
    def __init__(self, name, description, module_name, class_name=None):
        """
        Initialize a Game instance.

        Args:
            name (str): Name of the game.
            description (str): Description of the game.
            module_name (str): Module name for dynamic import.
            class_name (str, optional): Class name for dynamic import.
        """
        self.name = name
        self.description = description
        self.module_name = module_name
        self.class_name = class_name

    def launch(self, screen_width=None, screen_height=None, fullscreen=True):
        """
        Launch the game. For 'Tetris Math', dynamically imports and runs its main function.
        For other games, prints a placeholder message.

        Args:
            screen_width (int, optional): Screen width.
            screen_height (int, optional): Screen height.
            fullscreen (bool, optional): Whether to launch in fullscreen.

        Returns:
            bool: True if launched successfully, False otherwise.
        """
        try:
            # Dynamic import of the game module (avoid circular imports)
            if self.name == "Tetris Math":
                from games.TetrisMath.main import main as tetris_main  # noqa: E402
                tetris_main(
                    screen_width=screen_width,
                    screen_height=screen_height,
                    fullscreen=fullscreen
                )
                return True
            elif self.name == "Math Beats":
                from games.math_beats.math_beats import main as math_beats_main  # noqa: E402
                math_beats_main(
                    screen_width=screen_width,
                    screen_height=screen_height,
                    fullscreen=fullscreen
                )
                return True
            # For test: always try importlib if module_name is set
            if self.module_name:
                import importlib
                module = importlib.import_module(f"games.{self.module_name}")
                if hasattr(module, "main"):
                    module.main(
                        screen_width=screen_width,
                        screen_height=screen_height,
                        fullscreen=fullscreen
                    )
                return True
            # Placeholder for other games
            print(f"{self.name} is a placeholder.")
            return False
        except (ImportError, TypeError, Exception) as e:
            print(f"Error launching game {self.name}: {e}")
            return False
