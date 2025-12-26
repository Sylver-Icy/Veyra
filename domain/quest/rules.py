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
    elif level < 15:
        return ["Common", "Rare", "Epic"]
    else:
        return ["Common", "Rare", "Epic", "Legendary"]


def number_of_items_for_quest() -> int:
    """
    Decide how many items a delivery quest should request.

    Returns:
        int: Randomly chosen number of items (1 or 2)
    """
    return random.randint(1, 2)


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