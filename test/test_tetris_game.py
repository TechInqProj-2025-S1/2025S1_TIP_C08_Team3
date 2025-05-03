import pytest
import importlib
import pygame

@pytest.fixture(scope="session", autouse=True)
def pygame_init():
    pygame.init()
    yield
    pygame.quit()

tetris_mod = importlib.import_module('games.TetrisMath.tetris')
TetrisGame = getattr(tetris_mod, 'TetrisGame')

def test_tetris_game_init():
    game = TetrisGame(player_name='Tester', difficulty_mode='basic')
    assert game.grid_width == 10
    assert game.grid_height == 20
    assert game.current_piece is not None
    assert game.next_piece is not None

def test_valid_move():
    game = TetrisGame(player_name='Tester', difficulty_mode='basic')
    piece = game.current_piece
    assert game.valid_move(piece, piece.x, piece.y)
    # Move out of bounds
    assert not game.valid_move(piece, -10, 0)
    assert not game.valid_move(piece, 0, 100)

def test_add_to_grid_and_clear_lines():
    game = TetrisGame(player_name='Tester', difficulty_mode='basic')
    piece = game.current_piece
    game.add_to_grid(piece)
    # Fill a line
    for x in range(game.grid_width):
        game.grid[game.grid_height-1][x] = (255,255,255)
    game.clear_lines()
    assert game.lines_cleared >= 1

def test_trigger_math_challenge():
    game = TetrisGame(player_name='Tester', difficulty_mode='basic')
    game.trigger_math_challenge()
    assert game.state == 'math_challenge'

def test_add_garbage_line():
    game = TetrisGame(player_name='Tester', difficulty_mode='basic')
    before = [row[:] for row in game.grid]
    game.add_garbage_line()
    after = game.grid
    assert before != after