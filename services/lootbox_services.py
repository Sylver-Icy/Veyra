import random
from sqlalchemy.sql.expression import func
from models.inventory_model import Items, Inventory
from database.sessionmaker import Session
from services.inventory_services import give_item
from services.economy_services import add_gold
from utils.itemname_to_id import get_item_id_safe
from utils.embeds.lootboxembed import lootbox_embed_and_view

def open_box(user_id, lootbox: str):
    rewards = lootbox_reward(user_id, lootbox)
    return lootbox_embed_and_view(rewards)

def lootbox_reward(user_id: int,lootbox: str):
    """
    Generates the reward for opening a given lootbox and gives it to the user.

    Args:
        lootbox (str): The name of the lootbox (e.g., "wooden box").

    Returns:
        dict: A dictionary containing 'gold' (int) and 'items' (list of dicts),
              where each dict in 'items' has keys: 'item', 'rarity', and 'quantity'.

    Raises:
        ValueError: If the lootbox name is invalid.
    """
    lootbox = lootbox.strip().lower()

    drop_rates = {
        "wooden box": {"common": 88, "rare": 10, "epic": 2},
        "stone box": {"common": 67, "rare": 28, "epic": 5},
        "iron box": {"common": 48, "rare": 37, "epic": 15},
        "platinum box": {"common": 21, "rare": 50, "epic": 25, "legendary": 4}
    }

    box_config = drop_rates.get(lootbox)
    if not box_config:
        raise ValueError("Wrong box name")

    # Initialize the reward output structure
    reward_output = {
        "gold": 0,
        "items": []
    }

    # Determine how many rolls the lootbox will produce
    rolls = count_rolls(lootbox)

    # First roll always yields gold amount
    gold_amount = decide_gold(lootbox)
    reward_output["gold"] = gold_amount
    add_gold(user_id, gold_amount)


    # Keep track of items already picked to avoid duplicates
    picked_items = set()

    # For remaining rolls, select items based on rarity and quantity
    for _ in range(rolls - 1):
        rarity = random.choices(
            population=list(box_config.keys()),
            weights=list(box_config.values()),
            k=1
        )[0]

        # Attempt up to 10 times to find a unique item of chosen rarity
        for _ in range(10):
            reward_item = pick_random_item(rarity)
            if reward_item.item_name not in picked_items:
                picked_items.add(reward_item.item_name)
                break
        else:
            # Skip this roll if no unique item found after 10 tries
            continue

        item_quantity = count_amount(lootbox, rarity)

        reward_output["items"].append({
            "item": reward_item.item_name,
            "rarity": rarity,
            "description": reward_item.item_description,
            "icon": reward_item.item_icon,
            "quantity": item_quantity
        })
        #Give the selected items to the user
        give_item(user_id,reward_item.item_id,item_quantity, True)

    return reward_output


def pick_random_item(rarity: str):
    """
    Selects a random item of the specified rarity from the database.

    Args:
        rarity (str): Rarity of the item to pick (e.g., "Common", "Rare").

    Returns:
        str: The name of the randomly selected item, or "Unknown item" if none found.
    """
    rarity = rarity.capitalize()
    with Session() as session:
        item = session.query(Items).filter_by(item_rarity=rarity).order_by(func.random()).first()  # pylint: disable=not-callable
        return item if item else "Unknown item"


def decide_gold(lootbox: str):
    """
    Determines the gold reward for opening a specific lootbox.

    Args:
        lootbox (str): Name of the lootbox.

    Returns:
        int: Random gold amount within defined range for the lootbox.
    """
    gold_ranges = {
        "wooden box": (12, 32),
        "stone box": (60, 122),
        "iron box": (200, 310),
        "platinum box": (400, 800)
    }
    min_gold, max_gold = gold_ranges.get(lootbox, (0, 0))
    return random.randint(min_gold, max_gold)


def count_rolls(lootbox_name: str):
    """
    Determines the number of item rolls for a given lootbox.

    Args:
        lootbox_name (str): The name of the lootbox.

    Returns:
        int: Number of rolls (items) to be awarded.

    Raises:
        ValueError: If the lootbox name is unknown.
    """
    rolls = {
        "wooden box": {1: 85, 2: 15},
        "stone box": {1: 60, 2: 40},
        "iron box": {1: 13, 2: 70, 3: 17},
        "platinum box": {3: 33, 4: 38, 5: 20, 6: 9}
    }

    box_config = rolls.get(lootbox_name.lower())
    if box_config is None:
        raise ValueError(f"Unknown lootbox name: {lootbox_name}")

    result = random.choices(
        population=list(box_config.keys()),
        weights=list(box_config.values()),
        k=1
    )
    return result[0]


def count_amount(lootbox_name: str, rarity_of_item: str):
    """
    Determines the quantity of an item based on lootbox and item rarity.

    Args:
        lootbox_name (str): Name of the lootbox.
        rarity_of_item (str): Rarity of the item.

    Returns:
        int: Quantity of the item to be rewarded.

    Raises:
        ValueError: If lootbox or rarity is invalid.
    """
    amount_table = {
        "wooden box": {
            "common": (1, 2),
            "rare": (1, 1),
            "epic": (1, 1),
        },
        "stone box": {
            "common": (1, 3),
            "rare": (1, 2),
            "epic": (1, 1),
        },
        "iron box": {
            "common": (2, 5),
            "rare": (1, 3),
            "epic": (1, 2),
        },
        "platinum box": {
            "common": (4, 7),
            "rare": (3, 6),
            "epic": (1, 3),
            "legendary": (1, 1),
        }
    }

    box_data = amount_table.get(lootbox_name)
    if not box_data:
        raise ValueError(f"Unknown lootbox: {lootbox_name}")

    rarity_range = box_data.get(rarity_of_item)
    if not rarity_range:
        raise ValueError(f"{lootbox_name} cannot drop items of rarity: {rarity_of_item}")

    # Return a random amount within the allowed range for this rarity
    return random.randint(*rarity_range)


def user_lootbox_count(user_id: int, lootbox_name: str):
    """
    Queries the user's inventory to find how many of the specified lootbox they own.

    Args:
        user_id (int): The user's ID.
        lootbox_name (str): The lootbox name.

    Returns:
        int: Quantity of lootbox the user has, -1 if lootbox is unknown.
    """
    item_id, suggestions = get_item_id_safe(lootbox_name)
    if item_id is None:
        return -1

    with Session() as session:
        lootbox = session.query(Inventory).filter_by(
            user_id=user_id,
            item_id=item_id
        ).first()
        return item_id if lootbox else 0
