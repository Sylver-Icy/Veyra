LEVEL_EXP = {
    1: 0,
    2: 100,
    3: 350,
    4: 650,
    5: 100,
}


def max_sylphs_allowed(tree_lvl: int):
    if tree_lvl == 1:
        return 1
    elif tree_lvl == 2:
        return 2
    elif tree_lvl == 3:
        return 3
    else:
        return 4


def get_level_from_exp(exp: int) -> int:
    """Return tree level based on total EXP."""
    lvl = 1
    for level, required_exp in LEVEL_EXP.items():
        if exp >= required_exp:
            lvl = level
        else:
            break
    return lvl


def should_level_up(current_exp: int, gained_exp: int) -> bool:
    """Check if EXP gain triggers a level up."""
    old_level = get_level_from_exp(current_exp)
    new_level = get_level_from_exp(current_exp + gained_exp)
    return new_level > old_level