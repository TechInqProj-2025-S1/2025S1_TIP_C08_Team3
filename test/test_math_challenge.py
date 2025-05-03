
import pytest
import importlib
import pygame

@pytest.fixture(scope="session", autouse=True)
def pygame_init():
    pygame.init()
    yield
    pygame.quit()

math_mod = importlib.import_module('games.TetrisMath.math_challenge')
MathChallenge = getattr(math_mod, 'MathChallenge')

def test_generate_problem():
    mc = MathChallenge(difficulty=1)
    mc.generate_problem()
    assert mc.equation
    assert mc.answer is not None

def test_add_and_remove_digit():
    mc = MathChallenge(difficulty=1)
    mc.add_digit('3')
    assert mc.user_answer == '3'
    mc.remove_digit()
    assert mc.user_answer == ''

def test_check_answer():
    mc = MathChallenge(difficulty=1)
    mc.answer = 7
    mc.user_answer = '7'
    assert mc.check_answer('7')
    mc.user_answer = 'wrong'
    assert not mc.check_answer('wrong')

def test_reset():
    mc = MathChallenge(difficulty=2)
    mc.user_answer = '5'
    mc.reset()
    assert mc.user_answer == ''
