SMELTER_DESCRIPTIONS = {
    0: "You haven't unlocked the Smelter yet. Unlock it with `!unlock smelter`.",
    1: "Your furnace is Level 1. You can smelt Copper using 5 Coal. The flames struggle, but they obey.",
    2: "Your furnace is Level 2. You can smelt Copper using 4 Coal. The fire burns steadier.",
    3: "Your furnace is Level 3. You can smelt Iron using 4 Coal. The heat is finally respectable.",
    4: "Your furnace is Level 4. You can smelt Iron using 3 Coal. You’re getting good at this.",
    5: "Your furnace is Level 5. You can now smelt Silver using 3 Coal. Profit smells metallic.",
    6: "Your furnace is Level 6. You can smelt Silver using 2 Coal. Efficiency achieved.",
    7: "Your furnace is Level 7. You can smelt all metals using only 1 Coal. Absolute furnace supremacy."
}

INVENTORY_DESCRIPTIONS = {
    0: "You haven't unlocked Inventory upgrades yet. Unlock it with `!unlock inventory`.",
    1: "Your inventory is Level 1. You have 20 slots.",
    2: "Your inventory is Level 2. You have 30 slots.",
    3: "Your inventory is Level 3. You have 40 slots.",
    4: "Your inventory is Level 4. You have 55 slots.",
    5: "Your inventory is Level 5. You have 60 slots.",
    6: "Your inventory is Level 6. You have 68 slots.",
    7: "Your inventory is Level 7. You have 70 slots."
}

POCKET_DESCRIPTIONS = {
    0: "You haven't unlocked Pocket upgrades yet. Unlock it with `!unlock pockets`.",
    1: "Your pockets are Level 1.\n"
       "Stack Limits → Common: 10 | Rare: 5 | Epic: 1 | Legendary: 1 | Minerals: 20 | Lootboxes: 2",

    2: "Your pockets are Level 2.\n"
       "Stack Limits → Common: 20 | Rare: 10 | Epic: 3 | Legendary: 1 | Minerals: 30 | Lootboxes: 5",

    3: "Your pockets are Level 3.\n"
       "Stack Limits → Common: 40 | Rare: 15 | Epic: 5 | Legendary: 1 | Minerals: 35 | Lootboxes: 10",

    4: "Your pockets are Level 4.\n"
       "Stack Limits → Common: 50 | Rare: 20 | Epic: 7 | Legendary: 1 | Minerals: 40 | Lootboxes: 12",

    5: "Your pockets are Level 5.\n"
       "Stack Limits → Common: 100 | Rare: 25 | Epic: 10 | Legendary: 2 | Minerals: 50 | Lootboxes: 15"
}

BREWING_STAND_DESCRIPTIONS = {
    0: "You haven't unlocked the Brewing Stand yet. Unlock it with `!unlock brewing`.",
    1: "Your brewing stand is Level 1. You can brew Tier I potions.",
    2: "Your brewing stand is Level 2. You can brew Tier I and Tier II potions.",
    3: "Your brewing stand is Level 3. You can brew Tier I, Tier II, and Tier III potions."
}

BUILDING_DESCRIPTIONS = {
    "smelter": SMELTER_DESCRIPTIONS,
    "inventory": INVENTORY_DESCRIPTIONS,
    "pockets": POCKET_DESCRIPTIONS,
    "brewing stand": BREWING_STAND_DESCRIPTIONS
}


def get_building_description(building_name: str, level: int) -> str:
    building_name = building_name.lower()

    building_data = BUILDING_DESCRIPTIONS.get(building_name)
    if not building_data:
        return "Unknown building."

    description = building_data.get(level)
    if not description:
        return f"Blehhhh"

    return description