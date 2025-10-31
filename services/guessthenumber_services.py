import random

class Guess():
    def __init__(self,user):
        self.user = user

    def pick_number_range(self, stage):
        initial_int = random.randint(0,100)
        if stage == 1:
            return (initial_int, initial_int+1)
        elif stage == 2:
            return (initial_int, initial_int+4)
        elif stage == 3:
            return (initial_int, initial_int+9)
        else:
            return (initial_int, initial_int+19)

    def guess_number(self, low, high):
        return random.randint(low, high)

