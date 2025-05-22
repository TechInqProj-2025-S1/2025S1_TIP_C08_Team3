# Question grid logic
import random
from .constants import GRID_SIZE, EASY, NORMAL, HARD

class QuestionGrid:
    def __init__(self, difficulty):
        self.difficulty = difficulty
        self.grid = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.answers = []
        self.generate_questions()

    def generate_questions(self):
        operations = []
        if self.difficulty == EASY:
            operations = ["+"]
        elif self.difficulty == NORMAL:
            operations = ["+", "-"]
        elif self.difficulty == HARD:
            operations = ["+", "-", "*", "/"]
        self.grid = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        num_questions = random.randint(15, 20)
        possible_positions = [(i, j) for i in range(GRID_SIZE) for j in range(GRID_SIZE)]
        question_positions = random.sample(possible_positions, num_questions)
        unique_answers = set()
        for pos in question_positions:
            i, j = pos
            question, answer = self.generate_single_question(operations)
            self.grid[i][j] = (question, answer)
            unique_answers.add(answer)
        unique_answers_list = list(unique_answers)
        if len(unique_answers_list) <= 5:
            self.answers = unique_answers_list
        else:
            self.answers = random.sample(unique_answers_list, 5)
        self.answers.append("Other")

    def generate_single_question(self, operations):
        operation = random.choice(operations)
        if operation == "+":
            a = random.randint(1, 20)
            b = random.randint(1, 20)
            question = f"{a} + {b}"
            answer = a + b
        elif operation == "-":
            a = random.randint(1, 20)
            b = random.randint(1, a)
            question = f"{a} - {b}"
            answer = a - b
        elif operation == "*":
            a = random.randint(1, 10)
            b = random.randint(1, 10)
            question = f"{a} × {b}"
            answer = a * b
        elif operation == "/":
            b = random.randint(1, 10)
            a = b * random.randint(1, 10)
            question = f"{a} ÷ {b}"
            answer = a // b
        return question, answer
