# ---------------------------------------------------------------------------
# Friendship configuration & rules
# ---------------------------------------------------------------------------

# Friendship EXP thresholds mapped to titles.
# Keys represent minimum EXP required to reach that tier.
FRIENDSHIP_TIERS = {
    0: "Stranger",
    100: "Acquaintance",
    300: "Casual",
    700: "Friend",
    1200: "Close Friend",
    1800: "Bestie",
    2500: "Veyra's favourite 💖",
}

# Maximum friendship EXP that can be gained per day
DAILY_FRIENDSHIP_CAP = 50


# ---------------------------------------------------------------------------
# Daily gain rules
# ---------------------------------------------------------------------------

def can_gain_friendship_today(current_daily_exp: int) -> bool:
    """
    Check whether the user can still gain friendship EXP today.

    Args:
        current_daily_exp (int): Friendship EXP already gained today

    Returns:
        bool: True if under the daily cap, False otherwise
    """
    return current_daily_exp < DAILY_FRIENDSHIP_CAP


# ---------------------------------------------------------------------------
# Progress & title calculation
# ---------------------------------------------------------------------------

def friendship_title_and_progress(exp: int) -> tuple[str, float]:
    """
    Determine the user's friendship title and progress to the next tier.

    Args:
        exp (int): Total friendship EXP

    Returns:
        tuple[str, float]:
            - Current friendship title
            - Progress percentage toward the next tier (0–100)
    """
    thresholds = sorted(FRIENDSHIP_TIERS.keys())

    title = FRIENDSHIP_TIERS[0]
    next_level = None

    for index, threshold in enumerate(thresholds):
        if exp >= threshold:
            title = FRIENDSHIP_TIERS[threshold]
            if index + 1 < len(thresholds):
                next_level = thresholds[index + 1]
        else:
            break

    if next_level is not None:
        previous_level = max(t for t in thresholds if t <= exp)
        progress = (exp - previous_level) / (next_level - previous_level) * 100
    else:
        progress = 100.0

    return title, round(progress, 2)