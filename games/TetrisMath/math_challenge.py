import random

class MathChallenge:
    def __init__(self, difficulty=1):
        self.difficulty = difficulty
        self.user_answer = ""
        self.answered = False
        self.correct = False
        self.problem_type = None
        self.equation = ""
        self.answer = None
        self.generate_problem()

    def generate_problem(self):
        problem_types = ["add", "sub", "mul", "div", "equation"]
        if self.difficulty == 1:
            types = ["add", "sub"]
        elif self.difficulty == 2:
            types = ["add", "sub", "mul"]
        elif self.difficulty == 3:
            types = ["add", "sub", "mul", "div"]
        else:
            types = problem_types
        self.problem_type = random.choice(types)
        if self.problem_type == "add":
            a = random.randint(1, 20 * self.difficulty)
            b = random.randint(1, 20 * self.difficulty)
            self.equation = f"{a} + {b} = ?"
            self.answer = a + b
        elif self.problem_type == "sub":
            a = random.randint(1, 20 * self.difficulty)
            b = random.randint(1, a)
            self.equation = f"{a} - {b} = ?"
            self.answer = a - b
        elif self.problem_type == "mul":
            a = random.randint(2, 10 * self.difficulty)
            b = random.randint(2, 10 * self.difficulty)
            self.equation = f"{a} × {b} = ?"
            self.answer = a * b
        elif self.problem_type == "div":
            b = random.randint(2, 10 * self.difficulty)
            self.answer = random.randint(2, 10 * self.difficulty)
            a = self.answer * b
            self.equation = f"{a} ÷ {b} = ?"
        elif self.problem_type == "equation":
            a = random.randint(1, 10 * self.difficulty)
            x = random.randint(1, 10 * self.difficulty)
            b = random.randint(0, 10 * self.difficulty)
            c = a * x + b
            self.equation = f"{a}x + {b} = {c}; x = ?"
            self.answer = x

    def check_answer(self, user_input):
        try:
            user_value = int(user_input)
            self.correct = (user_value == self.answer)
            self.answered = True
            return self.correct
        except ValueError:
            return False

    def add_digit(self, digit):
        if len(self.user_answer) < 7:
            self.user_answer += digit

    def remove_digit(self):
        if self.user_answer:
            self.user_answer = self.user_answer[:-1]

    def reset(self, difficulty=None):
        if difficulty is not None:
            self.difficulty = difficulty
        self.generate_problem()
        self.user_answer = ""
        self.answered = False
        self.correct = False
