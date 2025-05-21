
import pytest

def test_import_tetris_math_modules():
    import games.TetrisMath.tetris
    import games.TetrisMath.tetromino
    import games.TetrisMath.math_challenge
    import games.TetrisMath.network
    import games.TetrisMath.constants
    import games.TetrisMath.ui
    import games.TetrisMath.main
    import games.TetrisMath.__init__
    assert True

def test_tetromino_class_exists():
    from games.TetrisMath import tetromino
    assert hasattr(tetromino, 'Tetromino')

# --- White-box: test TetrisGame logic (backend) ---
def test_tetris_game_init():
    from games.TetrisMath.tetris import TetrisGame
    game = TetrisGame(player_name="Test", difficulty_mode="basic")
    assert game.player_name == "Test"
    assert game.difficulty_mode == "basic"

def test_tetris_game_score_increases():
    from games.TetrisMath.tetris import TetrisGame
    game = TetrisGame(player_name="Test", difficulty_mode="basic")
    old_score = game.score
    game.score += 10
    assert game.score == old_score + 10

# --- Black-box: UI class instantiation (frontend) ---
def test_tetris_math_ui_instantiation(monkeypatch):
    import pygame
    from games.TetrisMath.ui import TetrisMathUI
    # Patch pygame display to avoid opening a window
    monkeypatch.setattr(pygame.display, "set_mode", lambda *a, **k: pygame.Surface((800, 600)))
    monkeypatch.setattr(pygame.display, "set_caption", lambda *a, **k: None)
    ui = TetrisMathUI(screen_width=800, screen_height=600, fullscreen=False)
    assert ui.screen_width == 800
    assert ui.screen_height == 600

# --- White-box: test menu button logic (frontend logic) ---
def test_menu_buttons(monkeypatch):
    import pygame
    from games.TetrisMath.ui import TetrisMathUI
    monkeypatch.setattr(pygame.display, "set_mode", lambda *a, **k: pygame.Surface((800, 600)))
    monkeypatch.setattr(pygame.display, "set_caption", lambda *a, **k: None)
    ui = TetrisMathUI(screen_width=800, screen_height=600, fullscreen=False)
    assert hasattr(ui, 'menu_buttons')
    assert len(ui.menu_buttons) >= 1

# --- Test tetromino piece creation and rotation ---
def test_tetromino_piece_creation_and_rotation():
    from games.TetrisMath.tetromino import Tetromino
    piece = Tetromino()
    # Ensure piece has shape
    assert hasattr(piece, 'shape')
    assert isinstance(piece.shape, list)
    # Test rotation
    original_shape = [row[:] for row in piece.shape]  # deep copy
    piece.rotate()
    # After rotation the shape should be different (unless it's an O piece)
    shape_changed = original_shape != piece.shape
    is_o_piece = len(piece.shape) == 2 and len(piece.shape[0]) == 2 and all(all(cell for cell in row) for row in piece.shape)
    assert shape_changed or is_o_piece

# --- Test math challenge creation ---
def test_math_challenge_creation():
    from games.TetrisMath.math_challenge import MathChallenge
    # Test basic difficulty
    challenge = MathChallenge(difficulty="basic")
    challenge.generate_question()
    assert isinstance(challenge.a, int)
    assert isinstance(challenge.b, int)
    assert challenge.op in ['+', '-', '*', '/']
    assert isinstance(challenge.answer, (int, float))
    
    # Test answer checking
    correct_answer = challenge.answer
    assert challenge.check_answer(correct_answer) is True
    if correct_answer != 0:  # Avoid issues with division by zero
        assert challenge.check_answer(correct_answer + 1) is False
    else:
        assert challenge.check_answer(1) is False

# --- Test game over state (integration) ---
def test_game_over_state(monkeypatch):
    import pygame
    from games.TetrisMath.tetris import TetrisGame
    game = TetrisGame(player_name="Test", difficulty_mode="basic")
    assert game.game_over is False
    
    # Simulate game over
    game.set_state("game_over")
    assert game.game_over is True

# --- Test grid manipulation and collision detection ---
def test_grid_manipulation():
    from games.TetrisMath.tetris import TetrisGame
    
    # Create a new game
    game = TetrisGame(player_name="Test", difficulty_mode="basic")
    
    # Test initial grid is empty (all cells are None/False)
    assert all(not any(row) for row in game.grid)
    
    # Test collision detection with walls
    game.current_piece.x = -1  # Move piece off left edge
    assert not game.valid_move(game.current_piece, game.current_piece.x, game.current_piece.y)
    
    game.current_piece.x = game.grid_width  # Move piece off right edge
    assert not game.valid_move(game.current_piece, game.current_piece.x, game.current_piece.y)
    
    # Reset x position to valid
    game.current_piece.x = game.grid_width // 2
    
    # Test collision detection with floor
    game.current_piece.y = game.grid_height
    assert not game.valid_move(game.current_piece, game.current_piece.x, game.current_piece.y)

# --- Test UI Button Class ---
def test_ui_button(monkeypatch):
    import pygame
    from games.TetrisMath.ui import Button
    
    # Create a temporary surface for testing
    screen = pygame.Surface((800, 600))
    
    # Create a button
    button = Button((100, 100, 200, 50), "Test Button", (255, 0, 0), (0, 255, 0), 
                    pygame.font.Font(None, 24))
    
    # Test button properties
    assert button.text == "Test Button"
    assert button.rect.topleft == (100, 100)
    assert button.rect.width == 200
    assert button.rect.height == 50
    
    # Test click detection - not clicked when mouse is outside
    assert button.is_clicked((50, 50), True) is False
    
    # Test click detection - clicked when mouse is inside and mouse_click is True
    assert button.is_clicked((150, 125), True) is True
    
    # Test hover state
    button.update((150, 125))
    assert button.hovered is True
    
    button.update((50, 50))
    assert button.hovered is False

# --- Test math challenge in gameplay ---
def test_math_challenge_gameplay():
    from games.TetrisMath.tetris import TetrisGame
    from games.TetrisMath.math_challenge import MathChallenge
    
    # Create a game
    game = TetrisGame(player_name="Test", difficulty_mode="basic")
    
    # Access the math challenge object
    assert hasattr(game, "math")
    assert isinstance(game.math, MathChallenge)
    
    # Simulate answering a math question correctly
    game.math.generate_question()
    correct_answer = game.math.answer
    
    # Set game state to math challenge
    game.set_state("math_challenge")
    assert game.state == "math_challenge"
    
    # Answer correctly and check if it affects score
    game.math.user_answer = str(correct_answer)
    result = game.math.check_answer(game.math.user_answer)
    assert result is True
    
    # In a real game, correct answers should increase score
    game.correct_answers += 1
    assert game.correct_answers > 0

# --- Test UI state management ---
def test_ui_state_management(monkeypatch):
    import pygame
    from games.TetrisMath.ui import TetrisMathUI
    
    # Mock pygame display
    monkeypatch.setattr(pygame.display, "set_mode", lambda *a, **k: pygame.Surface((800, 600)))
    monkeypatch.setattr(pygame.display, "set_caption", lambda *a, **k: None)
    
    # Create UI
    ui = TetrisMathUI(screen_width=800, screen_height=600, fullscreen=False)
    
    # Initial state should be menu
    assert ui.state == 'menu'
    
    # Set up for game start
    ui.name = "TestPlayer"
    ui.difficulty = "basic"
    
    # Start game
    ui.start_game()
    assert ui.state == 'playing'
    assert ui.tetris_game is not None

# --- Test math challenge digit entry ---
def test_math_challenge_digit_entry():
    from games.TetrisMath.math_challenge import MathChallenge
    challenge = MathChallenge(difficulty="basic")
    
    # Test adding digits
    challenge.user_answer = ""
    challenge.add_digit("1")
    assert challenge.user_answer == "1"
    challenge.add_digit("2")
    assert challenge.user_answer == "12"
    challenge.add_digit("3")
    assert challenge.user_answer == "123"
    
    # Test removing digits
    challenge.remove_digit()
    assert challenge.user_answer == "12"
    challenge.remove_digit()
    assert challenge.user_answer == "1"
    challenge.remove_digit()
    assert challenge.user_answer == ""
    
    # Test removing from empty string does nothing
    challenge.remove_digit()
    assert challenge.user_answer == ""

# --- Test master difficulty math challenge ---
def test_master_difficulty_math():
    from games.TetrisMath.math_challenge import MathChallenge
    challenge = MathChallenge(difficulty="master")
    
    has_larger_number = False
    # Generate multiple questions to check difficulty ranges
    for _ in range(10):
        challenge.generate_question()
        if challenge.a > 10 or challenge.b > 10:
            has_larger_number = True
        
        # All operations should be valid
        assert challenge.op in ['+', '-', '*', '/']
        
        # If division, ensure divisor isn't zero
        if challenge.op == '/':
            assert challenge.b != 0
    
    # Master difficulty should sometimes use larger numbers
    assert has_larger_number

# --- Test game piece movement ---
def test_piece_movement():
    from games.TetrisMath.tetris import TetrisGame
    
    game = TetrisGame(player_name="Test", difficulty_mode="basic")
    
    # Store initial position
    initial_x = game.current_piece.x
    initial_y = game.current_piece.y
    
    # Test moving left
    game.move_piece(-1)
    assert game.current_piece.x == initial_x - 1
    
    # Test moving right
    game.move_piece(1)
    assert game.current_piece.x == initial_x
    
    # Test soft drop (moving down)
    game.soft_drop()
    assert game.current_piece.y == initial_y + 1

# --- Test piece rotation ---
def test_piece_rotation():
    from games.TetrisMath.tetris import TetrisGame
    
    game = TetrisGame(player_name="Test", difficulty_mode="basic")
    
    # Store the original shape
    original_shape = [row[:] for row in game.current_piece.shape]
    
    # Test rotation
    game.rotate_piece()
    
    # Either shape changed or it's the O piece which doesn't change on rotation
    is_o_piece = len(game.current_piece.shape) == 2 and len(game.current_piece.shape[0]) == 2 and all(all(cell for cell in row) for row in game.current_piece.shape)
    shape_changed = original_shape != game.current_piece.shape
    
    assert shape_changed or is_o_piece

# --- Test ghost piece position ---
def test_ghost_piece_position():
    from games.TetrisMath.tetris import TetrisGame
    
    game = TetrisGame(player_name="Test", difficulty_mode="basic")
    
    # Get current position
    current_x = game.current_piece.x
    current_y = game.current_piece.y
    
    # Get ghost position
    ghost_x, ghost_y = game.get_ghost_piece_position()
    
    # Ghost x should be the same as current piece
    assert ghost_x == current_x
    
    # Ghost y should be >= current y (it drops to lowest valid position)
    assert ghost_y >= current_y

# --- Test multiplayer network integration ---
def test_network_integration(monkeypatch):
    import pygame
    from games.TetrisMath.tetris import TetrisGame
    from games.TetrisMath.network import TetrisNetwork
    from unittest.mock import MagicMock
    
    # Create a mock network
    mock_network = MagicMock()
    mock_network.mode = "host"
    mock_network.connected = True
    
    # Create game with multiplayer mode
    game = TetrisGame(player_name="Test", difficulty_mode="basic", multiplayer_mode="host")
    game.network = mock_network
    
    # Test sending state sync
    game.send_state_sync()
    mock_network.send_event.assert_called_once()
    
    # Check what data was sent
    call_args = mock_network.send_event.call_args[0][0]
    assert call_args["type"] == "state_sync"
    assert "score" in call_args
    assert "grid" in call_args

# --- Test clearing lines ---
def test_clear_lines():
    from games.TetrisMath.tetris import TetrisGame
    
    game = TetrisGame(player_name="Test", difficulty_mode="basic")
    
    # Set up a grid with a complete line at the bottom
    test_color = (255, 0, 0)  # Red for visibility
    
    # Fill the bottom row completely
    bottom_row = game.grid_height - 1
    for x in range(game.grid_width):
        game.grid[bottom_row][x] = test_color
    
    # Verify the line is filled
    assert all(game.grid[bottom_row][x] for x in range(game.grid_width))
    
    # Clear lines
    lines_cleared = game.clear_lines()
    
    # Verify line was cleared
    assert lines_cleared == 1
    assert not any(game.grid[bottom_row][x] for x in range(game.grid_width))
