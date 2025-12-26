import logging
import random

from sqlalchemy import select, func

from database.sessionmaker import Session
from domain.quest.rules import (
    allowed_rarities_for_level,
    number_of_items_for_quest,
    final_delivery_reward,
    can_skip,
)
from models.inventory_model import Items
from models.users_model import Quests
from services.exp_services import current_exp
from services.inventory_services import fetch_inventory, take_item
from utils.embeds.delieveryembed import delievery_embed
from utils.itemname_to_id import get_item_id_safe

logger = logging.getLogger(__name__)


def requested_items(user_name: str, user_id: int):
    """
    Entry point for the delivery mini-game.

    - If the user already has an active quest, reuse it.
    - Otherwise, generate a new quest.
    - Always returns a Discord embed representing the quest state.
    """
    # Fetch current streak (if quest exists)
    with Session() as session:
        quest = session.execute(
            select(Quests).where(Quests.user_id == user_id)
        ).scalar_one_or_none()
        streak = quest.streak if quest else 0

    quest = fetch_quest(user_id)

    if quest and quest.delivery_items:
        delivery_items_name_list = quest.delivery_items
        reward = quest.reward
    else:
        delivery_items_name_list, reward = create_quest(user_id)

    embed = delievery_embed(
        user_name,
        delivery_items_name_list,
        reward,
        user_id,
        streak,
    )
    return embed


def create_quest(user_id: int):
    """
    Creates or updates a delivery quest for the user.

    Flow:
    - Determine user level
    - Select allowed item rarities
    - Randomly pick 1–2 items
    - Calculate reward
    - Store quest in DB (update if exists, insert if new)

    Returns:
        tuple[list[str], int]: (item names, reward)
    """
    _, user_lvl = current_exp(user_id)

    with Session() as session:
        rarity_pool = allowed_rarities_for_level(user_lvl)
        num_items = number_of_items_for_quest()

        delivery_items = (
            session.execute(
                select(Items)
                .where(Items.item_rarity.in_(rarity_pool))
                .order_by(func.random())
                .limit(num_items)
            )
            .scalars()
            .all()
        )

        reward = calculate_reward(delivery_items, user_id)
        delivery_items_name_list = [item.item_name for item in delivery_items]

        existing_quest = session.execute(
            select(Quests).where(Quests.user_id == user_id)
        ).scalar_one_or_none()

        if existing_quest:
            existing_quest.delivery_items = delivery_items_name_list
            existing_quest.reward = reward
            existing_quest.limit += 1
        else:
            session.add(
                Quests(
                    user_id=user_id,
                    delivery_items=delivery_items_name_list,
                    reward=reward,
                    limit=0,
                    skips=0,
                )
            )

        session.commit()

    logger.info(
        "Quest created",
        extra={
            "user": user_id,
            "flex": f"Items requested -> {delivery_items_name_list}, Reward -> {reward}",
        },
    )

    return delivery_items_name_list, reward


def delete_quest(user_id: int, streak: bool = False):
    """
    Skips (deletes) the current quest for the user.

    Rules:
    - User can only skip if skip limit allows
    - Skipping resets items and reward
    - Streak is reset unless explicitly preserved

    Returns:
        bool: True if skipped successfully, False otherwise
    """
    with Session() as session:
        quest = session.execute(
            select(Quests).where(Quests.user_id == user_id)
        ).scalar_one_or_none()

        if not can_skip(quest.skips):
            return False

        quest.delivery_items = None
        quest.reward = 0
        quest.skips += 1

        if not streak:
            quest.streak = 0

        session.commit()

    logger.info("Quest skipped", extra={"user": user_id})
    return True


def fetch_quest(user_id: int):
    """
    Fetch the current quest for a user.

    Returns:
        Quests | None
    """
    with Session() as session:
        return session.execute(
            select(Quests).where(Quests.user_id == user_id)
        ).scalar_one_or_none()


def calculate_reward(items: list, user_id: int):
    """
    Calculate delivery reward based on item rarities and streak.

    Args:
        items (list[Items]): Items required for the quest
        user_id (int): User identifier

    Returns:
        int: Final calculated reward
    """
    rarities_list = [item.item_rarity for item in items]

    with Session() as session:
        quest = session.execute(
            select(Quests).where(Quests.user_id == user_id)
        ).scalar_one_or_none()
        streak = quest.streak if quest else 0

    return final_delivery_reward(rarities_list, streak)


def items_check(user_id: int, items: list):
    """
    Validate and complete a delivery quest.

    - Confirms user owns all required items
    - Deducts items only if validation passes
    - Increments streak on success

    Returns:
        bool: True if completed, False otherwise
    """
    inventory = fetch_inventory(user_id)
    owned_items = {
        item["item_name"]
        for item in inventory
        if item["item_quantity"] > 0
    }

    for item in items:
        if item not in owned_items:
            return False

    for item in items:
        item_id, _ = get_item_id_safe(item)
        take_item(user_id, item_id, 1)

    logger.info(
        "Quest completed",
        extra={
            "user": user_id,
            "flex": f"Items delivered -> {items}",
        },
    )

    with Session() as session:
        quest = session.get(Quests, user_id)
        quest.streak += 1
        session.commit()

    return True


def reset_skips():
    """
    Reset skip counters for all users.
    Intended for daily reset jobs.
    """
    with Session() as session:
        session.query(Quests).update({Quests.skips: 0})
        session.commit()

    logger.info("Quest skips reset for all users")