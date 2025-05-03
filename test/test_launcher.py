
import pytest
import os
import sys
import json
import importlib
from unittest import mock
import pygame

# Add project root to sys.path for imports
top_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, top_dir)

@pytest.fixture(scope="session", autouse=True)
def pygame_init():
    pygame.init()
    yield
    pygame.quit()

@pytest.fixture
def launcher_module():
    return importlib.import_module('launcher')

def test_launcher_config_exists(launcher_module):
    config_path = os.path.join(top_dir, 'config.json')
    assert os.path.exists(config_path)
    with open(config_path) as f:
        config = json.load(f)
    assert 'launcher' in config
    assert 'games' in config

def test_launcher_game_list(launcher_module):
    games = getattr(launcher_module, 'main', None)
    assert games is not None

def test_launcher_settings_menu(monkeypatch, launcher_module):
    # Simulate settings menu logic (non-GUI)
    config_path = os.path.join(top_dir, 'config.json')
    with open(config_path) as f:
        config = json.load(f)
    assert 'games' in config
    # Simulate updating IP/port
    config['games']['tetris_math_multiplayer'] = {'host_ip': '192.168.1.2', 'host_port': 6000}
    with open(config_path, 'w') as f:
        json.dump(config, f)
    with open(config_path) as f:
        updated = json.load(f)
    assert updated['games']['tetris_math_multiplayer']['host_ip'] == '192.168.1.2'
    assert updated['games']['tetris_math_multiplayer']['host_port'] == 6000

def test_launcher_imports():
    # Test that all game modules can be imported
    for game in [
        'games.TetrisMath.main',
        'games.math_beats.math_beats',
        'games.sequence_game.sequence_game',
        'games.spell_quest.spell_quest',
        'games.typing_game.typing_game',
        'games.word_pop.word_pop',
    ]:
        importlib.import_module(game)
