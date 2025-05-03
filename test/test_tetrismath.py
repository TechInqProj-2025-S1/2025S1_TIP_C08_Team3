import pytest
import os
import sys
import importlib
import json
from unittest import mock

top_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, top_dir)

@pytest.fixture
def tetris_math_module():
    return importlib.import_module('games.TetrisMath.main')

def test_import_tetris_math():
    mod = importlib.import_module('games.TetrisMath.main')
    assert hasattr(mod, 'main')

def test_constants():
    const = importlib.import_module('games.TetrisMath.constants')
    assert hasattr(const, 'GRID_WIDTH')
    assert hasattr(const, 'GRID_HEIGHT')
    # Accept either legacy TITLE_FONT or new get_fonts function
    assert hasattr(const, 'TITLE_FONT') or hasattr(const, 'get_fonts')

def test_math_challenge():
    math_mod = importlib.import_module('games.TetrisMath.math_challenge')
    MathChallenge = getattr(math_mod, 'MathChallenge')
    mc = MathChallenge(difficulty=2)
    mc.generate_problem()
    assert mc.equation
    assert mc.answer is not None
    mc.add_digit('5')
    assert mc.user_answer == '5'
    mc.remove_digit()
    assert mc.user_answer == ''
    mc.user_answer = str(mc.answer)
    assert mc.check_answer(mc.user_answer)
    mc.user_answer = 'wrong'
    assert not mc.check_answer(mc.user_answer)

def test_tetris_game_logic():
    tetris_mod = importlib.import_module('games.TetrisMath.tetris')
    TetrisGame = getattr(tetris_mod, 'TetrisGame')
    game = TetrisGame(player_name='Test', difficulty_mode='basic')
    assert game.grid_width > 0 and game.grid_height > 0
    piece = game.current_piece
    assert game.valid_move(piece, piece.x, piece.y)
    game.add_to_grid(piece)
    game.clear_lines()
    game.reset_game()
    game.trigger_math_challenge()
    assert game.state == 'math_challenge'

def test_network_send_event(monkeypatch):
    network_mod = importlib.import_module('games.TetrisMath.network')
    TetrisNetwork = getattr(network_mod, 'TetrisNetwork')
    net = TetrisNetwork('host', '127.0.0.1', 5001)
    net.conn = mock.Mock()
    net.send_event({'type': 'add_line'})
    net.conn.sendall.assert_called()

def test_ui_import():
    ui_mod = importlib.import_module('games.TetrisMath.ui')
    assert hasattr(ui_mod, 'TetrisMathUI')
