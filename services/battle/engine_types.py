from dataclasses import dataclass, field
from typing import Any


@dataclass
class CombatEvent:
    kind: str
    message: str
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass
class ActionResult:
    status: str
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass
class RoundResolution:
    text: str
    area_notes: list[str] = field(default_factory=list)
    events: list[CombatEvent] = field(default_factory=list)

    @property
    def display_text(self) -> str:
        if not self.area_notes:
            return self.text
        return "\n".join(self.area_notes + [self.text])


@dataclass
class RoundContext:
    manager: Any
    player1: Any
    player2: Any
    arena: Any = None
    round_number: int = 1

    def swapped(self) -> "RoundContext":
        return RoundContext(
            manager=self.manager,
            player1=self.player2,
            player2=self.player1,
            arena=self.arena,
            round_number=self.round_number,
        )


@dataclass
class SessionRoundOutcome:
    round_number: int
    p1_move: str
    p2_move: str
    p1_timed_out: bool
    p2_timed_out: bool
    resolution: RoundResolution
    penalty_notes: list[str] = field(default_factory=list)

    @property
    def result_text(self) -> str:
        if not self.penalty_notes:
            return self.resolution.display_text
        return self.resolution.display_text + "\n" + "\n".join(self.penalty_notes)


@dataclass
class BattleResultState:
    finished: bool
    both_dead: bool = False
    winner: Any = None
    loser: Any = None

