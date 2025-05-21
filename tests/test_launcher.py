
import pytest

def test_import_launcher_modules():
    import launcher.button
    import launcher.constants
    import launcher.game
    import launcher.menus
    import launcher.score
    import launcher.settings_menu
    import launcher.__init__
    assert True

def test_button_class_exists():
    from launcher import button
    assert hasattr(button, 'Button')

# --- White-box: test Game class logic (backend) ---
def test_game_class_init():
    from launcher.game import Game
    g = Game("TestGame", "desc", "module")
    assert g.name == "TestGame"
    assert g.description == "desc"
    assert g.module_name == "module"

# --- Black-box: Button UI logic (frontend logic) ---
def test_button_instantiation(monkeypatch):
    import pygame
    from launcher.button import Button
    monkeypatch.setattr(pygame.font, "SysFont", lambda *a, **k: pygame.font.Font(None, 24))
    btn = Button(0, 0, 100, 40, "Test")
    assert btn.text == "Test"
    assert btn.rect.width == 100
    assert btn.rect.height == 40

# --- Test launcher.game module (launch function) ---
def test_game_launch(monkeypatch):
    import sys
    from launcher.game import Game
    
    # Mock the importlib and module with main function
    class MockModule:
        def main(self, screen_width=None, screen_height=None, fullscreen=True):
            return True
    
    # Track if import_module was called with correct args
    import_called_with = None
    
    def mock_import_module(name):
        nonlocal import_called_with
        import_called_with = name
        module = MockModule()
        return module
    
    monkeypatch.setattr("importlib.import_module", mock_import_module)

    # Patch Game.launch to always call importlib.import_module
    # (in case placeholder logic is present)
    game = Game("TestGame", "Test Description", "test.module")
    # Remove placeholder main to force import
    if hasattr(game, "main"):
        delattr(game, "main")
    result = game.launch(screen_width=800, screen_height=600, fullscreen=False)

    # Verify module was imported correctly
    assert import_called_with == "games.test.module"
    assert result is True

# --- Test failed game launch ---
def test_game_launch_failure(monkeypatch):
    import sys
    from launcher.game import Game
    
    # Mock import_module to raise ImportError
    def mock_import_module_error(name):
        raise ImportError(f"Mock import error for {name}")
    
    monkeypatch.setattr("importlib.import_module", mock_import_module_error)
    
    # Create game and test failure handling
    game = Game("TestGame", "Test Description", "test.module")
    result = game.launch()
    
    # Should return False on error
    assert result is False

# --- Test Button click detection ---
def test_button_click_detection(monkeypatch):
    import pygame
    from launcher.button import Button
    
    # Mock pygame font
    monkeypatch.setattr(pygame.font, "SysFont", lambda *a, **k: pygame.font.Font(None, 24))
    
    # Create a button
    btn = Button(100, 100, 200, 50, "Test Button")
    
    # Test click detection with mouse inside button + click
    assert btn.is_clicked((150, 125), True) is True
    
    # Test click detection with mouse outside button + click
    assert btn.is_clicked((50, 50), True) is False
    
    # Test click detection with mouse inside button but no click
    assert btn.is_clicked((150, 125), False) is False

# --- Test Button rendering ---
def test_button_rendering(monkeypatch):
    import pygame
    from launcher.button import Button
    
    # Initialize pygame
    pygame.init()
    
    # Mock pygame font
    monkeypatch.setattr(pygame.font, "SysFont", lambda *a, **k: pygame.font.Font(None, 24))
    
    # Create a button and a surface to render on
    btn = Button(100, 100, 200, 50, "Test Button")
    surface = pygame.Surface((800, 600))
    
    # Test drawing the button
    btn.draw(surface)
    
    # Test hover state change
    assert btn.current_color == btn.color
    btn.update((150, 125))  # Mouse position inside button
    assert btn.hovered is True
    btn.draw(surface)
    
    btn.update((50, 50))  # Mouse position outside button
    assert btn.hovered is False
    btn.draw(surface)

# --- Test Game with custom class_name ---
def test_game_with_custom_class():
    from launcher.game import Game
    game = Game("TestGame", "desc", "module", class_name="CustomClass")
    assert game.name == "TestGame" 
    assert game.class_name == "CustomClass"

# --- Test high score functionality ---
def test_high_scores(monkeypatch):
    from launcher.score import get_high_scores
    import json
    
    # Sample test scores
    test_scores = [
        {"name": "Player1", "score": 1000, "difficulty": "basic"},
        {"name": "Player2", "score": 2000, "difficulty": "master"}
    ]
    
    # Mock open function using a context manager to handle file operations
    class MockOpen:
        def __init__(self, *args, **kwargs):
            pass
            
        def __enter__(self):
            return self
            
        def __exit__(self, *args):
            pass
            
        def read(self):
            return json.dumps(test_scores)
    
    # Patch the functions
    monkeypatch.setattr("builtins.open", MockOpen)
    monkeypatch.setattr("os.path.exists", lambda x: True)
    
    # Get scores
    scores = get_high_scores("tetris_math")
    
    # Validate scores
    assert len(scores) == 2
    assert scores[0]["name"] == "Player1"
    assert scores[0]["score"] == 1000
    assert scores[1]["name"] == "Player2"
    assert scores[1]["score"] == 2000

# --- Test empty high scores ---
def test_empty_high_scores(monkeypatch):
    from launcher.score import get_high_scores
    
    # Mock os.path.exists to return False (file doesn't exist)
    monkeypatch.setattr("os.path.exists", lambda x: False)
    
    # Get scores for non-existent file
    scores = get_high_scores("non_existent_game")
    
    # Should return empty list
    assert scores == []

# --- Test menus integration ---
def test_menus_high_scores(monkeypatch):
    import pygame
    from unittest.mock import MagicMock, patch
    from launcher.menus import show_high_scores_menu
    from launcher.game import Game
    
    # Create mock screen and clock
    screen = pygame.Surface((800, 600))
    clock = MagicMock()
    fonts = (pygame.font.Font(None, 60), pygame.font.Font(None, 36), 
             pygame.font.Font(None, 32), pygame.font.Font(None, 28))
    
    # Create some test games
    games = [Game("TestGame", "Test Description", "test.module")]
    
    # Mock pygame event handling to exit menu immediately, but also simulate a mouse click on the back button
    quit_called = {"value": False}
    orig_get = pygame.event.get
    def mock_event_get():
        if not quit_called["value"]:
            # Simulate a mouse click event
            quit_called["value"] = True
            event = MagicMock()
            event.type = pygame.MOUSEBUTTONDOWN
            return [event]
        else:
            # After first click, simulate QUIT to break any further loops
            event = MagicMock()
            event.type = pygame.QUIT
            return [event]
    monkeypatch.setattr(pygame.event, "get", mock_event_get)
    # Patch Button.is_clicked to always return True for back button
    from launcher import button as button_mod
    orig_is_clicked = button_mod.Button.is_clicked
    def always_true(self, mouse_pos, mouse_click):
        return True
    monkeypatch.setattr(button_mod.Button, "is_clicked", always_true)
    # Patch pygame.quit and sys.exit to prevent actual quitting
    monkeypatch.setattr(pygame, "quit", lambda: None)
    monkeypatch.setattr("sys.exit", lambda x=0: None)
    # Patch pygame.display.flip to avoid "Display mode not set" error
    monkeypatch.setattr(pygame.display, "flip", lambda: None)
    # Test menu function (should exit immediately due to mocked event)
    show_high_scores_menu(games, screen, clock, fonts)

# --- Test Button hover state ---
def test_button_hover_state():
    from launcher.button import Button
    import pygame
    
    # Create button
    btn = Button(100, 100, 200, 50, "Test Button")
    
    # Initial state should not be hovered
    assert btn.hovered is False
    
    # Update with mouse position inside button
    btn.update((150, 125))
    assert btn.hovered is True
    assert btn.current_color == btn.hover_color
    
    # Update with mouse position outside button
    btn.update((50, 50))
    assert btn.hovered is False
    assert btn.current_color == btn.color
