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
        # Math Flip stores scores as a dict by difficulty, flatten for launcher
        if game_name.lower().replace(' ', '_') == 'math_flip':
            # scores is a dict: {"Easy": [...], "Normal": [...], "Hard": [...]}
            flat_scores = []
            for difficulty, entries in scores.items():
                for entry in entries:
                    entry_copy = dict(entry)
                    entry_copy['difficulty'] = difficulty
                    flat_scores.append(entry_copy)
            return flat_scores
        return scores
    except (json.JSONDecodeError, OSError, AttributeError):
        return []

# --- Custom high score/leaderboard readers for other games ---
def get_spell_quest_leaderboard():
    path = "games/spell_quest/leaderboard.json"
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def get_sequence_game_high_score():
    path = "games/sequence_game/highscore.txt"
    if not os.path.exists(path):
        return 0
    try:
        with open(path, "r") as f:
            return int(f.read().strip())
    except Exception:
        return 0

def get_typing_game_leaderboard():
    path = "games/typing_game/leaderboard.json"
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def get_word_pop_high_score():
    path = "games/word_pop/highscore.txt"
    if not os.path.exists(path):
        return None, 0
    try:
        with open(path, "r") as f:
            line = f.readline().strip()
            if line:
                name, score = line.split(",")
                return name, int(score)
    except Exception:
        pass
    return None, 0
