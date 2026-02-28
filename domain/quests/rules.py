import random

QUESTS = {
    "battle_warrior": {
        "id": "battle_warrior",
        "type": "BATTLE_WIN",
        "name": "Seasoned Warrior",
        "description": "Win 10 battles.",
        "target": 10,
        "filters": {},  # reserved for future (enemy type, mode, etc.)
        "reward": {
            "gold": 300,
            "xp": 100
        },
        "duration_hours": 24
    },

    "battle_streak": {
        "id": "battle_streak",
        "type": "BATTLE_WIN_STREAK",
        "name": "Unstoppable",
        "description": "Win 5 battles in a row.",
        "target": 5,
        "filters": {},
        "reward": {
            "gold": 500,
            "xp": 200
        },
        "duration_hours": 24
    },

    "gold_grinder": {
        "id": "gold_grinder",
        "type": "GOLD_EARN",
        "name": "Gold Grinder",
        "description": "Earn 500 gold.",
        "target": 500,
        "filters": {},
        "reward": {
            "gold": 150,
            "xp": 80
        },
        "duration_hours": 24
    },

    "market_merchant": {
        "id": "market_merchant",
        "type": "ITEM_SELL",
        "name": "Market Merchant",
        "description": "Sell 7 items on the marketplace.",
        "target": 7,
        "filters": {},
        "reward": {
            "gold": 250,
            "xp": 120
        },
        "duration_hours": 24
    },

    "loot_hunter": {
        "id": "loot_hunter",
        "type": "LOOTBOX_OPEN",
        "name": "Loot Hunter",
        "description": "Open 3 lootboxes.",
        "target": 3,
        "filters": {},
        "reward": {
            "gold": 200,
            "xp": 90
        },
        "duration_hours": 24
    }
}

def get_random_quest(exclude_ids=None):
    """
    Return a random quest from QUESTS.

    Args:
        exclude_ids: Optional list of quest IDs to exclude from selection

    Returns:
        A random quest dictionary
    """
    exclude_ids = exclude_ids or []
    available_quests = [q for qid, q in QUESTS.items() if qid not in exclude_ids]
    return random.choice(available_quests)

def get_quest_by_id(quest_id):
    """
    Return a quest dictionary by its ID.

    Args:
        quest_id: The ID of the quest to retrieve

    Returns:
        The quest dictionary, or None if not found
    """
    return QUESTS.get(quest_id)