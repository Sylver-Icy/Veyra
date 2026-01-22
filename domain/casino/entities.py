from dataclasses import dataclass

@dataclass
class GameResult:
    won: bool
    delta: int            # +chips or -chips
    message: str
    meta: dict | None = None


@dataclass
class CasinoGame:
    id: str
    name: str
    min_bet: int
    max_bet: int
    play: callable