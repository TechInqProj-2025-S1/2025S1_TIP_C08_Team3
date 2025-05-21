
import pytest
import pygame

@pytest.fixture(autouse=True)
def pygame_init():
    pygame.init()
    yield
    pygame.quit()

@pytest.fixture
def mock_surface():
    return pygame.Surface((800, 600))

@pytest.fixture
def mock_display(monkeypatch):
    mock_screen = pygame.Surface((800, 600))
    monkeypatch.setattr(pygame.display, 'set_mode', lambda *a, **k: mock_screen)
    monkeypatch.setattr(pygame.display, 'set_caption', lambda *a, **k: None)
    return mock_screen

@pytest.fixture
def mock_font(monkeypatch):
    mock_font = pygame.font.Font(None, 24)
    monkeypatch.setattr(pygame.font, 'SysFont', lambda *a, **k: mock_font)
    return mock_font


@pytest.fixture
def tmp_config_file(tmp_path):
    """Create a temporary config file for testing."""
    import json
    config_path = tmp_path / "config.json"
    config_data = {
        "launcher": {
            "display": {"width": 800, "height": 600, "borderless": False}
        },
        "games": {
            "tetris_math_multiplayer": {
                "host_ip": "127.0.0.1",
                "host_port": 5000
            }
        }
    }
    with open(config_path, 'w') as f:
        json.dump(config_data, f)
    return config_path


@pytest.fixture
def mock_event_queue(monkeypatch):
    """Mock pygame event queue for testing UI interactions."""
    events = []
    
    def mock_get():
        nonlocal events
        result = events.copy()
        events.clear()
        return result
    
    def mock_post(event):
        nonlocal events
        events.append(event)
    
    monkeypatch.setattr(pygame.event, 'get', mock_get)
    monkeypatch.setattr(pygame.event, 'post', mock_post)
    
    return events

