"""
Casino games module.

Each game follows a delta-based payout model:
- delta > 0  -> player won chips (net gain)
- delta < 0  -> player lost chips
- delta == 0 -> no change

All games return a GameResult with:
(success: bool, delta: int, message: str)
"""

import random

from domain.casino.entities import CasinoGame, GameResult
from utils.emotes import CHIP_EMOJI


# ------------------------
# Flip Coin
# ------------------------
def flipcoin_game(bet: int, choice: str) -> GameResult:
    """
    Flip Coin:
    - Choice: heads / tails
    - Win: 2x payout
    """
    c = str(choice).strip().lower()

    if c in ("heads", "head"):
        choice_norm = "heads"
    elif c in ("tails", "tail"):
        choice_norm = "tails"
    else:
        return GameResult(
            False,
            0,
            "Pick **heads** or **tails**. This is a coin flip, not circus."
        )

    coin = random.choice(["heads", "tails"])
    won = choice_norm == coin

    if won:
        payout = bet * 2
        delta = payout - bet
        return GameResult(
            True,
            delta,
            f"🪙 It landed **{coin}**!\n"
            f"YAY!!. **Payout: {payout}{CHIP_EMOJI}**\n"
            "Flip Again!!!.",
            meta={"result": coin}
        )

    return GameResult(
        False,
        -bet,
        f"🪙 It landed **{coin}**.\n"
        f"Lost **-{bet}{CHIP_EMOJI}**. Cry about it.",
        meta={"result": coin}
    )


# ------------------------
# Roulette
# ------------------------
def roulette_game(bet: int, choice: str) -> GameResult:
    """
    Roulette (0–9):
    - Choice: number between 0 and 9
    - Win: 10x payout
    """
    choice_str = str(choice).strip()

    if not choice_str.isdigit():
        return GameResult(
            False,
            0,
            "Pick a number from **0–9**. Example: `roulette 50 7`"
        )

    picked = int(choice_str)
    if not 0 <= picked <= 9:
        return GameResult(
            False,
            0,
            "Number must be between **0 and 9**. The wheel is small."
        )

    rolled = random.randint(0, 9)

    if picked == rolled:
        payout = bet * 10
        delta = payout - bet
        return GameResult(
            True,
            delta,
            f"🎡 Wheel landed on **{rolled}**!\n"
            f"Unhinged accuracy. **10x payout** 💀🔥\n"
            f"You walk away with **{payout}{CHIP_EMOJI}**",
            meta={"rolled": rolled, "picked": picked}
        )

    return GameResult(
        False,
        -bet,
        f"🎡 Wheel landed on **{rolled}**.\n"
        f"You picked **{picked}**.\n"
        "Rip your chips.",
        meta={"rolled": rolled, "picked": picked}
    )


# ------------------------
# Slots
# ------------------------
def slots_game(bet: int, choice: str) -> GameResult:
    """
    Slots:
    - Triple match: high multiplier
    - Pair: partial win
    """
    symbols = ["🍒", "🍒", "🍒", "🍋", "🍋", "🍇", "🍇", "🔔", "⭐", "💎"]

    a = random.choice(symbols)
    b = random.choice(symbols)
    c = random.choice(symbols)

    spin = f"{a} {b} {c}"

    triple_mult = {
        "🍒": 5,
        "🍋": 4,
        "🍇": 4,
        "🔔": 8,
        "⭐": 12,
        "💎": 25,
    }

    if a == b == c:
        mult = triple_mult.get(a, 3)
        payout = bet * mult
        delta = payout - bet
        return GameResult(
            True,
            delta,
            f"🎰 **SLOTS** 🎰\n"
            f"{spin}\n"
            f"TRIPLE HIT DAMNN🔥😭 **x{mult}**\n"
            f"Paid out **{payout}{CHIP_EMOJI}**",
            meta={"reels": [a, b, c]}
        )

    if a == b or b == c or a == c:
        mult = 1.66
        payout = round(bet * mult)
        delta = payout - bet
        return GameResult(
            True,
            delta,
            f"🎰 **SLOTS** 🎰\n"
            f"{spin}\n"
            f"PAIR HIT ✨ **x{mult}**\n"
            f"You won **{payout}{CHIP_EMOJI}**",
            meta={"reels": [a, b, c]}
        )

    return GameResult(
        False,
        -bet,
        f"🎰 **SLOTS** 🎰\n"
        f"{spin}\n"
        f"Lost **-{bet}{CHIP_EMOJI}**.\n"
        "Machine remains unimpressed.",
        meta={"reels": [a, b, c]}
    )


# ------------------------
# Dungeon Raid
# ------------------------
def dungeon_game(bet: int, choice: str) -> GameResult:
    """
    Dungeon Raid:
    Risk increases with deeper areas, but so do rewards.
    """
    choice_norm = str(choice).strip().lower()

    DUNGEON_AREAS = {
        "caves": {"death": 0.20, "mult": 1.20, "name": "Safe Caves"},
        "tunnels": {"death": 0.35, "mult": 1.50, "name": "Goblin Tunnels"},
        "ruins": {"death": 0.50, "mult": 2.00, "name": "Ancient Ruins"},
        "lair": {"death": 0.70, "mult": 3.33, "name": "Dragon Lair"},
        "abyss": {"death": 0.85, "mult": 6.66, "name": "Abyss Gate"},
    }

    if choice_norm not in DUNGEON_AREAS:
        return GameResult(
            False,
            0,
            "Pick a dungeon: `caves`, `tunnels`, `ruins`, `lair`, `abyss`"
        )

    area = DUNGEON_AREAS[choice_norm]
    roll = random.random()

    if roll < area["death"]:
        return GameResult(
            False,
            -bet,
            f"🗡️ **DUNGEON RAID**\n"
            f"Area: **{area['name']}**\n"
            f"You triggered a trap and died 💀\n"
            f"Lost **-{bet}{CHIP_EMOJI}**",
            meta={"area": choice_norm, "outcome": "trap"}
        )

    payout = round(bet * area["mult"])
    delta = payout - bet

    return GameResult(
        True,
        delta,
        f"🗡️ **DUNGEON RAID**\n"
        f"Area: **{area['name']}**\n"
        f"Treasure secured 🎁✨\n"
        f"Multiplier: **x{area['mult']}**\n"
        f"Loot worth **{payout}{CHIP_EMOJI}**",
        meta={"area": choice_norm, "outcome": "win"}
    )


# ------------------------
# Game Registry
# ------------------------
GAMES: dict[str, CasinoGame] = {
    "flipcoin": CasinoGame(
        id="flipcoin",
        name="Flip Coin",
        min_bet=1,
        max_bet=5000,
        play=flipcoin_game,
    ),
    "roulette": CasinoGame(
        id="roulette",
        name="Roulette",
        min_bet=10,
        max_bet=2500,
        play=roulette_game,
    ),
    "slots": CasinoGame(
        id="slots",
        name="Slots",
        min_bet=10,
        max_bet=2000,
        play=slots_game,
    ),
    "dungeon": CasinoGame(
        id="dungeon",
        name="Dungeon",
        min_bet=10,
        max_bet=3000,
        play=dungeon_game,
    ),
}