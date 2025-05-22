import os
import json
import pytest
from games.MathFlip.constants import EASY, NORMAL, HARD, GRID_SIZE, SCORE_FILE
from games.MathFlip.highscore import initialize_highscores, load_highscores, save_highscores, update_highscores
from games.MathFlip.question import QuestionGrid

# Black box tests
def test_initialize_highscores_creates_file(tmp_path, monkeypatch):
    score_file = tmp_path / "math_flip_scores.json"
    monkeypatch.setattr('games.MathFlip.constants.SCORE_FILE', str(score_file))
    monkeypatch.setattr('games.MathFlip.highscore.SCORE_FILE', str(score_file))
    initialize_highscores()
    assert os.path.exists(score_file)
    with open(score_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    assert set(data.keys()) == {EASY, NORMAL, HARD}
    for v in data.values():
        assert v == []

def test_load_highscores_returns_dict(tmp_path, monkeypatch):
    score_file = tmp_path / "math_flip_scores.json"
    monkeypatch.setattr('games.MathFlip.constants.SCORE_FILE', str(score_file))
    monkeypatch.setattr('games.MathFlip.highscore.SCORE_FILE', str(score_file))
    initialize_highscores()
    scores = load_highscores()
    assert isinstance(scores, dict)
    assert set(scores.keys()) == {EASY, NORMAL, HARD}

def test_save_and_update_highscores(tmp_path, monkeypatch):
    score_file = tmp_path / "math_flip_scores.json"
    monkeypatch.setattr('games.MathFlip.constants.SCORE_FILE', str(score_file))
    monkeypatch.setattr('games.MathFlip.highscore.SCORE_FILE', str(score_file))
    initialize_highscores()
    update_highscores(EASY, "Alice", 10)
    update_highscores(EASY, "Bob", 20)
    scores = load_highscores()
    assert scores[EASY][0]["name"] == "Bob"
    assert scores[EASY][1]["name"] == "Alice"
    assert scores[EASY][0]["score"] == 20
    assert scores[EASY][1]["score"] == 10

# White box tests
def test_update_highscores_limit(tmp_path, monkeypatch):
    score_file = tmp_path / "math_flip_scores.json"
    monkeypatch.setattr('games.MathFlip.constants.SCORE_FILE', str(score_file))
    monkeypatch.setattr('games.MathFlip.highscore.SCORE_FILE', str(score_file))
    initialize_highscores()
    for i in range(10):
        update_highscores(EASY, f"P{i}", i)
    scores = load_highscores()
    assert len(scores[EASY]) == 5
    assert scores[EASY][0]["score"] == 9
    assert scores[EASY][-1]["score"] == 5

def test_question_grid_easy():
    qg = QuestionGrid(EASY)
    for row in qg.grid:
        for cell in row:
            if cell:
                question, answer = cell
                assert "+" in question
                assert isinstance(answer, int)
    assert all(isinstance(a, int) or a == "Other" for a in qg.answers)

def test_question_grid_normal():
    qg = QuestionGrid(NORMAL)
    for row in qg.grid:
        for cell in row:
            if cell:
                question, answer = cell
                assert any(op in question for op in ["+", "-"])
                assert isinstance(answer, int)
    assert all(isinstance(a, int) or a == "Other" for a in qg.answers)

def test_question_grid_hard():
    qg = QuestionGrid(HARD)
    for row in qg.grid:
        for cell in row:
            if cell:
                question, answer = cell
                assert any(op in question for op in ["+", "-", "×", "÷"])
                assert isinstance(answer, int)
    assert all(isinstance(a, int) or a == "Other" for a in qg.answers)

def test_question_grid_answers_length():
    for diff in [EASY, NORMAL, HARD]:
        qg = QuestionGrid(diff)
        assert 1 <= len(qg.answers) <= 6
        assert "Other" in qg.answers

def test_generate_single_question_all_ops():
    qg = QuestionGrid(HARD)
    ops = ["+", "-", "*", "/"]
    for op in ops:
        q, a = qg.generate_single_question([op])
        if op == "+":
            assert "+" in q and isinstance(a, int)
        elif op == "-":
            assert "-" in q and isinstance(a, int)
        elif op == "*":
            assert "×" in q and isinstance(a, int)
        elif op == "/":
            assert "÷" in q and isinstance(a, int)
            assert a * int(q.split("÷")[1].strip()) == int(q.split("÷")[0].strip())
