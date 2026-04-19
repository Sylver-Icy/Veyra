from services.battle.engine_types import BattleResultState, SessionRoundOutcome


class BattleSession:
    def __init__(self, manager, timeout_penalty: int = 25):
        self.manager = manager
        self.timeout_penalty = timeout_penalty

    @property
    def p1(self):
        return self.manager.p1

    @property
    def p2(self):
        return self.manager.p2

    def run_round(self, p1_move: str, p2_move: str):
        self.manager.execute_turn(p1_move, p2_move)
        return self.manager.resolve_round_result()

    def apply_timeout_penalties(
        self,
        p1_timed_out: bool,
        p2_timed_out: bool,
        p1_name: str,
        p2_name: str,
    ) -> list[str]:
        penalty_notes = []
        if p1_timed_out:
            self.p1.hp = max(0, self.p1.hp - self.timeout_penalty)
            penalty_notes.append(f"{p1_name} suffered an extra **-{self.timeout_penalty} HP** for hesitation.")
        if p2_timed_out:
            self.p2.hp = max(0, self.p2.hp - self.timeout_penalty)
            penalty_notes.append(f"{p2_name} suffered an extra **-{self.timeout_penalty} HP** for hesitation.")
        return penalty_notes

    def apply_round_effects(self) -> list[str]:
        notes = (self.p1.proc_effect() or []) + (self.p2.proc_effect() or [])
        return [note for note in notes if isinstance(note, str) and note.strip()]

    def process_round(
        self,
        round_number: int,
        p1_move: str,
        p2_move: str,
        p1_timed_out: bool,
        p2_timed_out: bool,
        p1_name: str,
        p2_name: str,
    ) -> SessionRoundOutcome:
        resolution = self.run_round(p1_move, p2_move)
        self.apply_timeout_penalties(p1_timed_out, p2_timed_out, p1_name, p2_name)
        penalty_notes = self.apply_round_effects()
        return SessionRoundOutcome(
            round_number=round_number,
            p1_move=p1_move,
            p2_move=p2_move,
            p1_timed_out=p1_timed_out,
            p2_timed_out=p2_timed_out,
            resolution=resolution,
            penalty_notes=penalty_notes,
        )

    def get_result_state(self) -> BattleResultState:
        if self.p1.hp <= 0 and self.p2.hp <= 0:
            return BattleResultState(finished=True, both_dead=True)
        if self.p1.hp <= 0:
            return BattleResultState(finished=True, winner=self.p2, loser=self.p1)
        if self.p2.hp <= 0:
            return BattleResultState(finished=True, winner=self.p1, loser=self.p2)
        return BattleResultState(finished=False)
