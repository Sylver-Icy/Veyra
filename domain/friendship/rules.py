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

    if not thresholds:
        return "Stranger", 0.0

    # Clamp negative values and handle max-tier users up front so callers never
    # need to worry about looking for a "next" tier that does not exist.
    safe_exp = max(0, exp)
    max_threshold = thresholds[-1]

    if safe_exp >= max_threshold:
        return FRIENDSHIP_TIERS[max_threshold], 100.0

    current_threshold = thresholds[0]
    next_threshold = thresholds[1]

    for threshold, following_threshold in zip(thresholds, thresholds[1:]):
        if safe_exp >= threshold:
            current_threshold = threshold
            next_threshold = following_threshold
        else:
            break

    current_title = FRIENDSHIP_TIERS[current_threshold]
    progress = (safe_exp - current_threshold) / (next_threshold - current_threshold) * 100
    progress = max(0.0, min(progress, 100.0))

    return current_title, round(progress, 2)
