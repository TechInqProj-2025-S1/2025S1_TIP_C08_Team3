"""Game launching logic"""

class Game:
    # Game entry for launcher
    # pylint: disable=too-few-public-methods
    def __init__(self, name, description, module_name, class_name=None):
        # Init Game
        self.name = name
        self.description = description
        self.module_name = module_name
        self.class_name = class_name

    def launch(self, screen_width=None, screen_height=None, fullscreen=True):
        # Launch the game
        try:
            # Dynamic import for Tetris Math
            if self.name == "Tetris Math":
                import pygame
                screen = pygame.display.get_surface()
                from games.TetrisMath.main import main as tetris_main  # noqa: E402
                tetris_main(
                    screen_width=screen_width,
                    screen_height=screen_height,
                    fullscreen=fullscreen,
                    screen=screen
                )
                return True
            elif self.name == "Math Flip":
                import pygame
                screen = pygame.display.get_surface()
                try:
                    from games.MathFlip import main as mathflip_main  # noqa: E402
                    mathflip_main(screen=screen)
                except ImportError:
                    from games.MathFlip.voltorb import launch_math_flip  # noqa: E402
                    launch_math_flip()
                return True

            # Launch other games as subprocess
            if self.name not in ("Tetris Math", "Math Flip"):
                import subprocess
                import sys
                import os
                # Map game names to their script paths
                script_paths = {
                    "Sequence Game": os.path.join(os.path.dirname(__file__), "..", "games", "sequence_game", "sequence.py"),
                    "Spell Quest": os.path.join(os.path.dirname(__file__), "..", "games", "spell_quest", "spell_quest.py"),
                    "Typing Game": os.path.join(os.path.dirname(__file__), "..", "games", "typing_game", "typing_game.py"),
                    "Word Pop": os.path.join(os.path.dirname(__file__), "..", "games", "word_pop", "python_balloon_pop.py"),
                }
                if self.name in script_paths:
                    script_path = os.path.abspath(script_paths[self.name])
                    subprocess.Popen([sys.executable, script_path])
                    return True
            # Fallback: importlib
            import importlib
            import pygame
            screen = pygame.display.get_surface()
            if self.module_name:
                try:
                    module = importlib.import_module(f"games.{self.module_name}")
                    if hasattr(module, "main"):
                        module.main(
                            screen_width=screen_width,
                            screen_height=screen_height,
                            fullscreen=fullscreen
                        )
                    return True
                except Exception as e:
                    print(f"Error launching game {self.name}: {e}")
                    return False

            # Placeholder
            print(f"{self.name} is a placeholder.")
            return False
        except (ImportError, TypeError, Exception) as e:
            print(f"Error launching game {self.name}: {e}")
            return False
