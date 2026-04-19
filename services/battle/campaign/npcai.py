import random
from collections import deque

from services.battle.constants import VALID_STANCES


class BaseAI:
    """
    Base class for all campaign NPC AIs.
    Handles shared utilities like weighted choice and opponent move history.
    """

    def __init__(self, fighter, opponent):
        self.fighter = fighter
        self.opponent = opponent

        # Track opponent move history for pattern detection
        if not hasattr(self.opponent, "move_history"):
            self.opponent.move_history = deque(maxlen=5)

    def weighted_choice(self, weights):
        """
        Choose a stance based on weighted probabilities.
        Order: attack, block, counter, recover, cast
        """
        return random.choices(
            list(VALID_STANCES),
            weights=weights,
            k=1
        )[0]
