import pytest

def test_score_loading():
    """Load file."""
    from launcher.score import get_high_scores
    
    # Using mock to avoid actual file operations
    with pytest.MonkeyPatch().context() as monkeypatch:
        # Mock os.path.exists to return True
        monkeypatch.setattr("os.path.exists", lambda x: True)
        
        # Mock open function to return sample score data
        import json
        test_scores = [{"name": "TestPlayer", "score": 100}]
        monkeypatch.setattr("builtins.open", 
                           lambda *args, **kwargs: 
                           type("MockFile", (), {
                               "read": lambda self: json.dumps(test_scores),
                               "__enter__": lambda self: self,
                               "__exit__": lambda self, *args: None,
                           })())
        
        scores = get_high_scores("test_game")
        
        # Verify the results
        assert len(scores) == 1
        assert scores[0]["name"] == "TestPlayer"
        assert scores[0]["score"] == 100

def test_score_loading_no_file():
    """No file."""
    from launcher.score import get_high_scores
    
    with pytest.MonkeyPatch().context() as monkeypatch:
        # Mock os.path.exists to return False
        monkeypatch.setattr("os.path.exists", lambda x: False)
        
        scores = get_high_scores("nonexistent_game")
        assert scores == []

