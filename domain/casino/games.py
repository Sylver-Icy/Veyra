"""
Casino games module providing various gambling games with a delta-based payout model.

Each game function accepts a bet amount and a choice parameter, and returns a GameResult.
The delta in GameResult represents net change to player's chips:
- Positive delta means player won chips (including original bet).
- Negative delta means player lost chips (bet lost).
- Zero delta means no chips won or lost.

Available games include: flip coin, roulette, slots, and dungeon raid.
"""

import random

from domain.casino.entities import GameResult, CasinoGame

from utils.emotes import CHIP_EMOJI


def flipcoin_game(bet: int, choice: str) -> GameResult:
    """
    Flip Coin game:
    - bet: amount wagered
    - choice: 'heads' or 'tails' (case insensitive, accepts singular/plural)
    Returns GameResult with delta representing net chip change.
    """
    c = str(choice).strip().lower()
    if c in ("heads", "head"):
        choice_norm = "heads"
    elif c in ("tails", "tail"):
        choice_norm = "tails"
    else:
        return GameResult(False, 0, "PICK BETWEEN HEADS OR TAILS\nThis is coin flip not circus.")

    coin = random.choice(["heads", "tails"])
    won = (choice_norm == coin)

    if won:
        payout = bet * 2
        delta = payout - bet
        return GameResult(
            True,
            delta,
            f"🪙 It landed **{coin}**! You made your chips double!!!! **Payout {payout}{CHIP_EMOJI}**\nYOU ARE SLAYING!!! Flip againnnnnnn"
        )

    return GameResult(False, -bet, f"🪙 It landed **{coin}**. You lost all your chips.\nCry about it")


def roulette_game(bet: int, choice: str) -> GameResult:
    """
    Roulette game (0-9):
    - bet: amount wagered
    - choice: number as string between 0 and 9 inclusive
    Returns GameResult with 10x payout on hit, loss otherwise.
    """
    choice_str = str(choice).strip()

    if not choice_str.isdigit():
        return GameResult(False, 0, "Pick a number from **0 to 9**. Example: `!gamble roulette 50 7`")

    picked = int(choice_str)
    if picked < 0 or picked > 9:
        return GameResult(False, 0, "Pick a number from **0 to 9**. Not rocket science.")

    rolled = random.randint(0, 9)
    won = (picked == rolled)

    if won:
        payout = bet * 10
        delta = payout - bet
        return GameResult(
            True,
            delta,
            f"🎡 The wheel stopped at **{rolled}**!\n"
            f"YOU ABSOLUTE MENACE 😭🔥 **10x** payout!\n"
            f"You made **{payout}{CHIP_EMOJI} just like that**"
        )

    return GameResult(
        False,
        -bet,
        f"🎡 The wheel stopped at **{rolled}**.\n"
        f"You picked **{picked}**.\n"
        f"We know what that means right?\n"
        "Sad...."
    )


def slots_game(bet: int, choice: str) -> GameResult:
    """
    Slots game:
    - bet: amount wagered
    - choice: unused, present for consistency
    Returns GameResult with payouts for triples, pairs, or loss.
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
        "💎": 25
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
            f"TRIPLE HIT 😭🔥 **x{mult}**\n"
            f"Crediting... **{payout}{CHIP_EMOJI}**"
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
            f"PAIR! **x{mult}** YESSSSS LET THE CHIPS MULTIPLY!!!\n"
            f"You won **{payout}{CHIP_EMOJI}**\n"
            f"LET'S GO AGAIN THIS TIME JACKPOT!!!"
        )

    return GameResult(
        False,
        -bet,
        f"🎰 **SLOTS** 🎰\n"
        f"{spin}\n"
        f"You lost **-{bet}{CHIP_EMOJI}**.\n"
        f"Skill issue. Spin again."
    )


def dungeon_game(bet: int, choice: str) -> GameResult:
    """
    Dungeon Raid game:
    - bet: amount wagered
    - choice: dungeon area string (caves, tunnels, ruins, lair, abyss)
    Returns GameResult with risk/reward based on area chosen.
    """
    choice_norm = str(choice).strip().lower()

    if choice_norm not in ["caves", "tunnels", "ruins", "lair", "abyss"]:
        return GameResult(
            False,
            0,
            "Pick a dungeon area: `caves`, `tunnels`, `ruins`, `lair`, `abyss` \nCheck `!details gambling` for more info."
        )

    DUNGEON_AREAS = {
        "caves": {"death": 0.20, "mult": 1.20, "name": "Safe Caves"},
        "tunnels": {"death": 0.35, "mult": 1.50, "name": "Goblin Tunnels"},
        "ruins": {"death": 0.50, "mult": 2.00, "name": "Ancient Ruins"},
        "lair": {"death": 0.70, "mult": 3.33, "name": "Dragon Lair"},
        "abyss": {"death": 0.85, "mult": 6.66, "name": "Abyss Gate"},
    }

    area = DUNGEON_AREAS[choice_norm]
    death = area["death"]
    mult = area["mult"]
    name = area["name"]

    roll = random.random()

    if roll < death:
        return GameResult(
            False,
            -bet,
            f"🗡️ **DUNGEON RAID**\n"
            f"Area: **{name}**\n"
            f"You triggered a trap and got deleted from existence 💀\n"
            f"Lost **-{bet}{CHIP_EMOJI}**\n"
            f"Skill issue. Respawn and try again."
        )

    payout = round(bet * mult)
    delta = payout - bet

    return GameResult(
        True,
        delta,
        f"🗡️ **DUNGEON RAID**\n"
        f"Area: **{name}**\n"
        f"You found a treasure chest!! 🎁✨\n"
        f"Multiplier: **x{mult}**\n"
        f"Loot inside is worth **{payout}{CHIP_EMOJI}**"
    )


# Dictionary of available games keyed by game id
GAMES: dict[str, CasinoGame] = {
    # Flip Coin game registration
    "flipcoin": CasinoGame(
        id="flipcoin",
        name="Flip Coin",
        min_bet=1,
        max_bet=5000,
        play=flipcoin_game
    ),

    # Roulette (0-9) game registration
    "roulette": CasinoGame(
        id="roulette",
        name="Roulette",
        min_bet=10,
        max_bet=2500,
        play=roulette_game
    ),

    # Slots game registration
    "slots": CasinoGame(
        id="slots",
        name="Slots",
        min_bet=10,
        max_bet=2000,
        play=slots_game
    ),

    # Dungeon Raid game registration
    "dungeon": CasinoGame(
        id="dungeon",
        name="Dungeon",
        min_bet=10,
        max_bet=3000,
        play=dungeon_game
    )
}