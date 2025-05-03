import pytest
import importlib
import pygame
from unittest import mock

@pytest.fixture(scope="session", autouse=True)
def pygame_init():
    pygame.init()
    yield
    pygame.quit()

network_mod = importlib.import_module('games.TetrisMath.network')
TetrisNetwork = getattr(network_mod, 'TetrisNetwork')

def test_network_host_and_send(monkeypatch):
    net = TetrisNetwork('host', '127.0.0.1', 5002)
    net.conn = mock.Mock()
    net.send_event({'type': 'add_line'})
    net.conn.sendall.assert_called()

def test_network_client_and_send(monkeypatch):
    net = TetrisNetwork('join', '127.0.0.1', 5002)
    net.conn = mock.Mock()
    net.send_event({'type': 'add_line'})
    net.conn.sendall.assert_called()

def test_network_close():
    net = TetrisNetwork('host', '127.0.0.1', 5002)
    net.conn = mock.Mock()
    net.sock = mock.Mock()
    net.close()
    net.conn.close.assert_called()
    net.sock.close.assert_called()
