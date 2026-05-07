"""Inventory rules and progression tables.

This module defines:
- Inventory slot progression by inventory level.
- Allowed stack sizes by pockets level and item type.

All functions are defensive: unknown levels/types fall back to 0.
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

# Maximum number of items allowed per stack, by pockets level and item type.
ALLOWED_TYPE_STACK = {
    1: {"item": 10, "potion": 1, "mineral": 20, "lootbox": 2, "shard": 50},
    2: {"item": 20, "potion": 2, "mineral": 30, "lootbox": 5, "shard": 100},
    3: {"item": 40, "potion": 3, "mineral": 35, "lootbox": 10, "shard": 200},
    4: {"item": 50, "potion": 4, "mineral": 40, "lootbox": 12, "shard": 300},
    5: {"item": 100, "potion": 5, "mineral": 50, "lootbox": 15, "shard": 500},
}

# Backwards-compatible name for existing imports.
ALLOWED_ITEM_STACK = ALLOWED_TYPE_STACK

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

def allowed_stack_size(pockets_lvl: int, item_type: str) -> int:
    """Return allowed stack size for an item at a given pockets level.

    Args:
        pockets_lvl: The player's pockets upgrade level.
        item_type: Item type/category name (e.g., "item", "shard", "mineral").

    Returns:
        The maximum stack size allowed for that type at that pockets level.
        Returns 0 if pockets level or type is unknown/invalid.
    """
    # Fetch rules for this pockets level; unknown levels have no rules.
    mapped_rules = ALLOWED_TYPE_STACK.get(pockets_lvl)
    if not mapped_rules:
        return 0

    item_type = item_type.lower().strip()

    # Defensive lookup: unknown item types should not crash the bot.
    return mapped_rules.get(item_type, 0)
