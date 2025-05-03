import pytest
import importlib
import sys
import os
from unittest import mock
import pygame

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

@pytest.fixture(scope="session", autouse=True)
def pygame_init():
    pygame.init()
    yield
    pygame.quit()

def get_ui():
    # Try both 'games.TetrisMath.ui' and 'TetrisMath.ui' for import flexibility
    mod_names = ['games.TetrisMath.ui', 'TetrisMath.ui']
    for mod_name in mod_names:
        if mod_name in sys.modules:
            del sys.modules[mod_name]
        try:
            ui_mod = importlib.import_module(mod_name)
            return getattr(ui_mod, 'TetrisMathUI')
        except ModuleNotFoundError:
            continue
    raise ImportError('Could not import TetrisMathUI from any known module path')

def test_cancel_connecting_overlay(monkeypatch):
    print('test_cancel_connecting_overlay running')
    TetrisMathUI = get_ui()
    ui = TetrisMathUI()
    ui.state = 'connecting'
    ui.multiplayer_mode = 'join'
    ui.network = mock.Mock()
    # Simulate mouse over and click on cancel button
    sw, sh = ui.screen_width, ui.screen_height
    mouse_pos = (sw//2, sh//2 + 100)
    mouse_click = True
    ui.draw_connecting_overlay(mouse_pos, mouse_click)
    assert ui.state == 'menu'
    assert ui.network is None
    assert ui.multiplayer_mode is None

def test_cancel_waiting_overlay(monkeypatch):
    print('test_cancel_waiting_overlay running')
    TetrisMathUI = get_ui()
    ui = TetrisMathUI()
    ui.state = 'waiting'
    ui.multiplayer_mode = 'host'
    ui.network = mock.Mock()
    # Simulate mouse over and click on cancel button
    sw, sh = ui.screen_width, ui.screen_height
    mouse_pos = (sw//2, sh//2 + 100)
    mouse_click = True
    ui.draw_waiting_overlay(mouse_pos, mouse_click)
    assert ui.state == 'menu'
    assert ui.network is None
    assert ui.multiplayer_mode is None
