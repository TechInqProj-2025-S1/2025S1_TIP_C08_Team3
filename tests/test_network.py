import pytest
from unittest.mock import MagicMock, patch

def test_network_initialization():
    from games.TetrisMath.network import TetrisNetwork
    
    # Mock callback function
    mock_callback = MagicMock()
    
    # Create network with host mode
    network = TetrisNetwork("host", "127.0.0.1", 5000, mock_callback)
    
    # Verify initialization
    assert network.mode == "host"
    assert network.host_ip == "127.0.0.1"
    assert network.host_port == 5000
    assert network.on_event == mock_callback
    assert not network.connected

