import random

# ---------------------------------------------------------------------------
# Configuration constants
# ---------------------------------------------------------------------------

# Base reward ranges for each item rarity.
# Format: rarity -> (min_reward, max_reward)
RARITY_REWARDS = {
    "Common": (10, 15),
    "Rare": (25, 32),
    "Epic": (71, 93),
    "Legendary": (181, 321),
    "Paragon": (799, 1211),
}

REROLL_COST = {
        0: 25,
        1: 75,
        2: 150,
        3: 300,
        4: 500
    }

# Maximum number of skips allowed per reset period
MAX_SKIPS = 3


# ---------------------------------------------------------------------------
# Rarity & quest generation rules
# ---------------------------------------------------------------------------

def allowed_rarities_for_level(level: int) -> list[str]:
    """
    Determine which item rarities are allowed for a given player level.

    Args:
        level (int): Player level

    Returns:
        list[str]: List of allowed rarity names
    """
    if level < 5:
        return ["Common"]
    elif level < 10:
        return ["Common", "Rare"]
    elif level < 18:
        return ["Common", "Rare", "Epic"]
    else:
        return ["Common", "Rare", "Epic", "Legendary"]


def number_of_items_for_quest(slots_used: int) -> int:
    """
    Decide how many items a delivery quest should request
    based on how many inventory slots the player is currently using.

    Args:
        slots_used (int): Number of inventory slots currently occupied

    Returns:
        int: Number of items the quest should request
    """
    if slots_used < 20:
        return 1
    elif 20 <= slots_used < 40:
        return 2
    elif 40 <= slots_used < 50:
        return 3
    elif 50 <= slots_used < 55:
        return 4
    elif 55 <= slots_used < 60:
        return 5
    elif 60 <= slots_used < 65:
        return 6
    else:
        return 7


# ---------------------------------------------------------------------------
# Reward calculation logic
# ---------------------------------------------------------------------------

def base_reward_for_rarities(rarities: list[str]) -> int:
    """
    Calculate the base reward for a list of item rarities.

    Each rarity contributes a random value within its configured range.

    Args:
        rarities (list[str]): List of item rarity names

    Returns:
        int: Total base reward
    """
    total = 0

    for rarity in rarities:
        low, high = RARITY_REWARDS[rarity]
        total += random.randint(low, high)

    return total


def streak_multiplier(streak: int) -> float:
    """
    Calculate the reward multiplier based on the user's delivery streak.

    Args:
        streak (int): Current delivery streak

    Returns:
        float: Multiplier applied to the final reward
    """
    if streak < 2:
        return 1.0
    elif streak < 6:
        return 1.2
    elif streak < 10:
        return 1.5
    else:
        return 2.0


def final_delivery_reward(rarities: list[str], streak: int) -> int:
    """
    Calculate the final delivery reward.

    Combines:
    - Base reward from item rarities
    - Random bonus multiplier
    - Streak multiplier

    Args:
        rarities (list[str]): Item rarities involved in the quest
        streak (int): Current delivery streak

    Returns:
        int: Final reward amount
    """
    base = base_reward_for_rarities(rarities)
    bonus = random.uniform(1.2, 1.8)

    return int(base * bonus * streak_multiplier(streak))


# ---------------------------------------------------------------------------
# Skip rules
# ---------------------------------------------------------------------------

def can_skip(skips: int) -> bool:
    """
    Check whether the user is allowed to skip a delivery quest.

    Args:
        skips (int): Number of skips already used

    Returns:
        bool: True if skipping is allowed, False otherwise
    """
    return skips < MAX_SKIPS

def quantity_for_level(level: int) -> int:
    """
    Decide how many of each item is required for a quest
    based on player level.

    <10  -> 1
    10-14 -> 2
    15-17 -> 3
    18-20 -> 4
    21-23 -> 6
    24-25+ -> 10
    """
    if level < 10:
        return 1
    elif level < 15:
        return 2
    elif level < 18:
        return 3
    elif level < 21:
        return 4
    elif level < 24:
        return 6
    else:
        return 10