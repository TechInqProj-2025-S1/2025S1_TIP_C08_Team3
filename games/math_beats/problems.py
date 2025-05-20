import random
import operator

# Operator sets by BPM
OPERATOR_SETS = {
    'fast': [('+', operator.add)],
    'medium': [('+', operator.add), ('-', operator.sub)],
    'slow': [('+', operator.add), ('-', operator.sub), ('×', operator.mul)],
}

def get_operator_set(bpm):
    if bpm >= 120:
        return OPERATOR_SETS['fast']
    elif bpm >= 80:
        return OPERATOR_SETS['medium']
    else:
        return OPERATOR_SETS['slow']

def generate_problem(bpm):
    ops = get_operator_set(bpm)
    op_sym, op_func = random.choice(ops)
    if op_sym == '×':
        a, b = random.randint(2, 9), random.randint(2, 9)
    elif op_sym == '-':
        a, b = random.randint(5, 20), random.randint(1, 15)
        if b > a:
            a, b = b, a
    else:
        a, b = random.randint(1, 20), random.randint(1, 20)
    answer = op_func(a, b)
    # Distractors
    distractors = set()
    while len(distractors) < 2:
        delta = random.choice([-2, -1, 1, 2])
        val = answer + delta
        if val != answer and val >= 0:
            distractors.add(val)
    choices = list(distractors) + [answer]
    random.shuffle(choices)
    return {'a': a, 'b': b, 'op': op_sym, 'answer': answer, 'choices': choices}
