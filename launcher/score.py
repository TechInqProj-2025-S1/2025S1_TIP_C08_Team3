"""Module for handling high scores for games."""
import os
import json

def get_high_scores(game_name):
    """
    Retrieve high scores for a given game from a JSON file.

    Args:
        game_name (str): The name of the game.

    Returns:
        list: A list of high scores, or an empty list if not found or on error.
    """
    score_file = f"scores/{game_name.lower().replace(' ', '_')}_scores.json"
    if not os.path.exists(score_file):
        return []
    try:
        with open(score_file, 'r', encoding='utf-8') as f:
            scores = json.load(f)
        return scores
    except (json.JSONDecodeError, OSError):
        return []
