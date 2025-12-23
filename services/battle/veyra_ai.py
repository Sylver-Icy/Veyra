import random

class VeyraAI:
    def __init__(self, difficulty="normal"):
        self.difficulty = difficulty

    def choose_move(self):
        return random.choices(
            ["attack", "block", "counter", "recover"],
            weights=[40, 20, 20, 20]
        )[0]