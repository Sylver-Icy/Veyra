from services.battle.engine_types import RoundContext
from services.battle.round_resolution import resolve_round


class BattleManager:
    """
    Manages the battle between two players by executing their moves each turn
    and resolving the outcomes based on their stances and stats.

    Responsibilities:
    - Set player stances and process effects each turn.
    - Resolve the round by determining damage, defense, counters, recoveries, and spell casts.
    - Determine the winner or if the battle results in a tie.
    """

    def __init__(self, player1, player2):
        self.p1 = player1
        self.p2 = player2
        self.round = 1
        self.arena = None

    def execute_turn(self, p1_move, p2_move):
        self.p1.set_stance(p1_move)
        self.p1.move_history.append(p1_move)
        self.p2.set_stance(p2_move)
        self.p2.move_history.append(p2_move)

    def resolve_round_result(self):
        self.round += 1
        ctx = RoundContext(
            manager=self,
            player1=self.p1,
            player2=self.p2,
            arena=self.arena,
            round_number=self.round,
        )
        return resolve_round(ctx)

    def resolve_round(self):
        return self.resolve_round_result().display_text
