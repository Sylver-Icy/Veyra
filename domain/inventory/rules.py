"""Inventory rules and progression tables.

This module defines:
- Inventory slot progression by inventory level.
- Allowed stack sizes by pockets level and item rarity.

All functions are defensive: unknown levels/rarities fall back to 0.
"""

# Total inventory slots unlocked at each inventory level.
INVENTORY_SLOTS = {
    1: 20,
    2: 30,
    3: 40,
    4: 55,
    5: 60,
    6: 68,
    7: 70
}

# Maximum number of items allowed per stack, by pockets level and item rarity.
ALLOWED_ITEM_STACK = {
    1: {"Common": 10, "Rare": 5, "Epic": 1, "Legendary": 1, "Minerals": 20, "Lootboxes":2},
    2: {"Common": 20, "Rare": 10, "Epic": 3, "Legendary": 1, "Minerals": 30, "Lootboxes":5},
    3: {"Common": 40, "Rare": 15, "Epic": 5, "Legendary": 1, "Minerals": 35, "Lootboxes":10},
    4: {"Common": 50, "Rare": 20, "Epic": 7, "Legendary": 1, "Minerals": 40, "Lootboxes":12},
    5: {"Common": 100, "Rare": 25, "Epic": 10, "Legendary": 2, "Minerals": 50, "Lootboxes":15}
}

def available_inventory_slots_for_user(inventory_lvl: int) -> int:
    """Return the number of inventory slots available for a given inventory level.

    Args:
        inventory_lvl: The player's inventory upgrade level.

    Returns:
        The number of unlocked inventory slots.
        Returns 0 if the level is unknown/invalid.
    """
    # Defensive default prevents KeyError and makes invalid levels safe.
    return INVENTORY_SLOTS.get(inventory_lvl, 0)

def allowed_stack_size(pockets_lvl: int, item_rarity: str) -> int:
    """Return allowed stack size for an item at a given pockets level.

    Args:
        pockets_lvl: The player's pockets upgrade level.
        item_rarity: Item rarity/category name (e.g., "Common", "Epic", "Minerals").

    Returns:
        The maximum stack size allowed for that rarity at that pockets level.
        Returns 0 if pockets level or rarity is unknown/invalid.

    Notes:
        - Rarity strings are normalized via `capitalize()`.
          This converts "legendary" -> "Legendary" (good).
    """
    # Fetch rules for this pockets level; unknown levels have no rules.
    mapped_rules = ALLOWED_ITEM_STACK.get(pockets_lvl)
    if not mapped_rules:
        return 0

    # Normalize input so callers can pass "legendary" etc.
    item_rarity = item_rarity.capitalize()

    # Defensive lookup: unknown rarities should not crash the bot.
    return mapped_rules.get(item_rarity, 0)