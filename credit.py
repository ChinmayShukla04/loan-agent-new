import random

def get_credit_score():
    # more realistic distribution
    return random.choice(
        list(range(300, 600)) * 2 +   # more low scores
        list(range(600, 750)) * 3 +   # medium scores
        list(range(750, 900)) * 5     # high scores
    )