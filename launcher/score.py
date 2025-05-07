import os
import json

def get_high_scores(game_name):
    score_file = f"scores/{game_name.lower().replace(' ', '_')}_scores.json"
    if not os.path.exists(score_file):
        return []
    
    try:
        with open(score_file, 'r') as f:
            scores = json.load(f)
        return scores
    except Exception:
        return []
