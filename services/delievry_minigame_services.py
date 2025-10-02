import logging
from sqlalchemy import select, func
import random

from models.inventory_model import Items
from models.users_model import Quests
from database.sessionmaker import Session
from utils.embeds.delieveryembed import delievery_embed
from utils.itemname_to_id import get_item_id_safe
from services.inventory_services import fetch_inventory, take_item

logger = logging.getLogger(__name__)

def requested_items(user_name: str, user_id: int):
    """
    Checks if the user has an assigned quest.
    If already assigned, returns the existing quest embed.
    Otherwise, creates a new quest and returns its embed.
    TODO: make it scale with user level
    """
    quest = fetch_quest(user_id)
    if quest and quest.delivery_items:
        delivery_items_name_list = quest.delivery_items
        reward = quest.reward
    else:
        delivery_items_name_list, reward = create_quest(user_id)

    embed = delievery_embed(user_name, delivery_items_name_list, reward, user_id)
    return embed


def create_quest(user_id: int):
    """
    Creates a delivery quest:
    - Picks 1 or 2 random common items from the database
    - Calculates reward based on items
    - Adds or updates quest in DB
    """
    with Session() as session:
        # Pick 1-2 random common items
        delivery_items = session.execute(
            select(Items)
            .where(Items.item_rarity == "Common")
            .order_by(func.random())
            .limit(random.randint(1, 2))
        ).scalars().all()

        reward = calculate_reward(delivery_items)
        delivery_items_name_list = [item.item_name for item in delivery_items]

        # Check if user already has a quest
        existing_quest = session.execute(
            select(Quests).where(Quests.user_id == user_id)
        ).scalar_one_or_none()

        if existing_quest:
            existing_quest.delivery_items = delivery_items_name_list
            existing_quest.reward = reward
            existing_quest.limit += 1
        else:
            new_quest = Quests(
                user_id=user_id,
                delivery_items=delivery_items_name_list,
                reward=reward,
                limit=0,  # Daily quest counter
                skips=0
            )
            session.add(new_quest)

        session.commit()  # Commit once after updates/adds
    logger.info("Quest created", extra={
        "user": user_id,
        "flex": f"Items requested-> {delivery_items_name_list}, Reward-> {reward}"
    })
    return delivery_items_name_list, reward


def delete_quest(user_id: int):
    """
    Deletes a quest for the user if skips < 3.
    Increments skip count and resets delivery items/reward.
    Returns True if skipped successfully, False otherwise.
    TODO: add logging
    """
    with Session() as session:
        quest = session.execute(
            select(Quests).where(Quests.user_id == user_id)
        ).scalar_one_or_none()

        if quest.skips >= 3:
            return False

        quest.delivery_items = None
        quest.reward = 0
        quest.skips += 1
        session.commit()
        logger.info("Quest skipped", extra={"user": user_id})
        return True


def fetch_quest(user_id: int):
    """
    Fetches the existing quest for a user.
    Returns None if no quest exists.
    """
    with Session() as session:
        return session.execute(
            select(Quests).where(Quests.user_id == user_id)
        ).scalar_one_or_none()


def calculate_reward(items: list):
    """
    Calculates the reward for a delivery quest based on item rarities.
    """
    RARITY_REWARDS = {
        "Common": (10, 15),
        "Rare": (25, 32),
        "Epic": (71, 93),
        "Legendary": (181, 321),
        "Paragon": (799, 1211)
    }

    total = 0
    for item in items:
        low, high = RARITY_REWARDS[item.item_rarity]
        total += random.randint(low, high)

    bonus = random.uniform(1.1, 1.7)  # Only round at the end for smoother scaling
    return int(total * bonus)


def items_check(user_id: int, items: list):
    """
    Checks if the user has all required items in inventory.
    If yes, deducts them and returns True.
    Otherwise, returns False without deducting anything.
    """
    inventory = fetch_inventory(user_id)
    items_set = {item["item_name"] for item in inventory if item["item_quantity"] > 0}

    # Check first
    for item in items:
        if item not in items_set:
            return False

    # Deduct after check
    for item in items:
        item_id, _ = get_item_id_safe(item)
        take_item(user_id, item_id, 1)
    logger.info("Quest completed", extra={
        "user": user_id,
        "flex": f"Items delievered-> {items}"
    })
    return True


def reset_skips():
    """
    Resets skip counters for all users.
    TODO: add logging
    """
    with Session() as session:
        session.query(Quests).update({Quests.skips: 0})
        session.commit()
    logger.info("Quest skips got reset")