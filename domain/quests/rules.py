import random

QUESTS = {
    "battle_warrior": {
        "id": "battle_warrior",
        "type": "BATTLE_WIN",
        "name": "Seasoned Warrior",
        "description": "Prove your mettle on the battlefield. Win 10 PvP or campaign battles within 24 hours to claim your reward.",
        "target": 7,
        "filters": {},
        "reward": [
            {"type": "gold", "amount": 500},
            {"type": "xp", "amount": 100},
            {"type": "item", "item_id": 177, "item_name": "Stone Box", "amount": 1}
        ],
        "duration_hours": 24
    },

    "battle_streak": {
        "id": "battle_streak",
        "type": "BATTLE_WIN_STREAK",
        "name": "Unstoppable",
        "description": "Go on a rampage! Win 5 battles in a row without a single loss. One defeat resets your progress.",
        "target": 5,
        "filters": {},
        "reward": [
            {"type": "gold", "amount": 250},
            {"type": "xp", "amount": 200},
            {"type": "item", "item_id": 178, "item_name": "Iron Box", "amount": 1}
        ],
        "duration_hours": 24
    },

    "gold_grinder": {
        "id": "gold_grinder",
        "type": "GOLD_EARN",
        "name": "Gold Grinder",
        "description": "Stack that coin! Earn a total of 500 gold from jobs, battles, sales, or any other source within 7 hours.",
        "target": 500,
        "filters": {},
        "reward": [
            {"type": "gold", "amount": 150},
            {"type": "xp", "amount": 80}
        ],
        "duration_hours": 7
    },

    "market_merchant": {
        "id": "market_merchant",
        "type": "ITEM_SELL",
        "name": "Market Merchant",
        "description": "Set up shop and move some inventory. Have 7 of your marketplace listings purchased by other players within 24 hours.",
        "target": 7,
        "filters": {},
        "reward": [
            {"type": "gold", "amount": 250},
            {"type": "xp", "amount": 120},
            {"type": "item", "item_id": 176, "item_name": "Wooden Box", "amount": 2}
        ],
        "duration_hours": 24
    },

    "loot_hunter": {
        "id": "loot_hunter",
        "type": "LOOTBOX_OPEN",
        "name": "Loot Hunter",
        "description": "Crack open 3 lootboxes of any tier — wooden, stone, iron, or platinum. Who knows what treasures await?",
        "target": 3,
        "filters": {},
        "reward": [
            {"type": "gold", "amount": 100},
            {"type": "xp", "amount": 90}
        ],
        "duration_hours": 24
    },

    # --- Gold variants ---

    "pocket_change": {
        "id": "pocket_change",
        "type": "GOLD_EARN",
        "name": "Pocket Change",
        "description": "Scrape together 200 gold via any means — jobs, battles, marketplace sales, or even gambling. Every coin counts.",
        "target": 200,
        "filters": {},
        "reward": [
            {"type": "gold", "amount": 80},
            {"type": "xp", "amount": 40}
        ],
        "duration_hours": 4
    },

    "big_spender": {
        "id": "big_spender",
        "type": "GOLD_SPEND",
        "name": "Big Spender",
        "description": "Splash the cash! Spend a total of 1000 gold on shop purchases, marketplace buys, upgrades, or casino bets within 24 hours.",
        "target": 1000,
        "filters": {},
        "reward": [
            {"type": "xp", "amount": 100},
            {"type": "item", "item_id": 177, "item_name": "Stone Box", "amount": 1}
        ],
        "duration_hours": 24
    },

    # --- Crafting / Alchemy ---

    "apprentice_smelter": {
        "id": "apprentice_smelter",
        "type": "SMELT",
        "name": "Apprentice Smelter",
        "description": "Fire up the smelter and forge 5 bars from raw ore. You'll need coal and ore in your inventory to get started.",
        "target": 5,
        "filters": {},
        "reward": [
            {"type": "xp", "amount": 90},
            {"type": "item", "item_id": 187, "item_name": "Coal", "amount": 10}
        ],
        "duration_hours": 3
    },

    "potion_brewer": {
        "id": "potion_brewer",
        "type": "BREW_POTION",
        "name": "Potion Brewer",
        "description": "Channel your inner alchemist and brew 3 potions at the brewing stand. Gather your ingredients and get mixing!",
        "target": 3,
        "filters": {},
        "reward": [
            {"type": "gold", "amount": 220},
            {"type": "xp", "amount": 110}
        ],
        "duration_hours": 24
    },

    # --- Jobs ---

    "hard_worker": {
        "id": "hard_worker",
        "type": "JOB_COMPLETE",
        "name": "Hard Worker",
        "description": "Put in the hours! Complete 8 jobs of any kind — knight, digger, miner, explorer, or thief — within 15 hours.",
        "target": 5,
        "filters": {},
        "reward": [
            {"type": "gold", "amount": 100},
            {"type": "xp", "amount": 100},
            {"type": "item", "item_id": 176, "item_name": "Wooden Box", "amount": 1}
        ],
        "duration_hours": 15
    },

    # --- Battle variants ---

    "first_blood": {
        "id": "first_blood",
        "type": "BATTLE_WIN",
        "name": "First Blood",
        "description": "Step into the arena and score 3 victories",
        "target": 3,
        "filters": {},
        "reward": [
            {"type": "gold", "amount": 120},
            {"type": "xp", "amount": 50}
        ],
        "duration_hours": 4
    },

    # --- Gambling ---

    "high_roller": {
        "id": "high_roller",
        "type": "CASINO_PLAY",
        "name": "High Roller",
        "description": "Hit the casino floor and play 5 games — flipcoin, roulette, or any table. Win or lose, every play counts.",
        "target": 5,
        "filters": {},
        "reward": [
            {"type": "gold", "amount": 150},
            {"type": "xp", "amount": 70}
        ],
        "duration_hours": 2
    },

    # --- Marketplace ---

    "bargain_hunter": {
        "id": "bargain_hunter",
        "type": "ITEM_BUY",
        "name": "Bargain Hunter",
        "description": "Browse the marketplace and snag 3 deals from other players. Keep an eye out for underpriced gems!",
        "target": 3,
        "filters": {},
        "reward": [
            {"type": "gold", "amount": 180},
            {"type": "xp", "amount": 85}
        ],
        "duration_hours": 12
    },

    # --- Lootbox variant ---

    "box_addict": {
        "id": "box_addict",
        "type": "LOOTBOX_OPEN",
        "name": "Box Addict",
        "description": "Can't stop, won't stop. Rip open 7 lootboxes of any tier within 4 hours. Fortune favors the bold.",
        "target": 7,
        "filters": {},
        "reward": [
            {"type": "gold", "amount": 400},
            {"type": "xp", "amount": 180},
            {"type": "item", "item_id": 179, "item_name": "Platinum Box", "amount": 1}
        ],
        "duration_hours": 4
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