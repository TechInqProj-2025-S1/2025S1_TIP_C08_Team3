# Highscore logic
import os
import json
from .constants import SCORE_FILE, EASY, NORMAL, HARD

def initialize_highscores():
    if not os.path.exists(SCORE_FILE):
        empty_scores = {
            EASY: [],
            NORMAL: [],
            HARD: []
        }
        os.makedirs(os.path.dirname(SCORE_FILE), exist_ok=True)
        with open(SCORE_FILE, 'w', encoding='utf-8') as f:
            json.dump(empty_scores, f)

def load_highscores():
    try:
        with open(SCORE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        initialize_highscores()
        return load_highscores()

def save_highscores(highscores):
    with open(SCORE_FILE, 'w', encoding='utf-8') as f:
        json.dump(highscores, f)

def update_highscores(difficulty, player_name, score):
    highscores = load_highscores()
    highscores[difficulty].append({"name": player_name, "score": score})
    highscores[difficulty] = sorted(highscores[difficulty], key=lambda x: x["score"], reverse=True)[:5]
    save_highscores(highscores)
