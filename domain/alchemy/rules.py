from difflib import get_close_matches

from services.upgrade_services import building_lvl

from domain.alchemy.potion_recipes import POTION_RECIPES

def can_craft_potion_tier(user_id: int, potion_tier: int, session):
    """
    Checks if user's brewing stand level allows crafting this potion tier.

    Brewing Stand rules:
    lvl 1 -> tier 1 potions
    lvl 2 -> tier 1-2 potions
    lvl 3 -> tier 1-3 potions
    """

    if session is None:
        raise ValueError("External session required")


    stand_level = building_lvl(user_id, "brewing stand", session=session)

    if stand_level == 0:
        return False  # user doesn't own brewing stand

    if potion_tier is None:
        return False

    return stand_level >= potion_tier


def resolve_potion(user_input):
    """
    Returns:
        (True, potion_key)
        (False, error_message)
    """

    # -------------------------
    # 1) ID lookup (int or numeric string)
    # -------------------------
    if isinstance(user_input, int) or str(user_input).isdigit():
        pid = int(user_input)

        for name, data in POTION_RECIPES.items():
            if data["id"] == pid:
                return True, name

        return False, f"No potion exists with ID {pid}."

    # -------------------------
    # 2) Name lookup
    # -------------------------
    normalized = str(user_input).strip().upper()
    upper_map = {k.upper(): k for k in POTION_RECIPES.keys()}

    # Exact
    if normalized in upper_map:
        return True, upper_map[normalized]

    # Fuzzy
    matches = get_close_matches(normalized, upper_map.keys(), n=1, cutoff=0.6)

    if matches:
        real_name = upper_map[matches[0]]
        pid = POTION_RECIPES[real_name]["id"]

        return False, (
            f"Potion not found. Closest match: **{real_name}** (ID: {pid})\n"
            f"You can brew using: `/brew {pid}`"
        )

    return False, "Potion not found."