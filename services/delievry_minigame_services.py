import logging
import random

from sqlalchemy import select, func

from database.sessionmaker import Session
from domain.quest.rules import (
    allowed_rarities_for_level,
    number_of_items_for_quest,
    quantity_for_level,
    final_delivery_reward,
    can_skip,
    REROLL_COST
)
from models.inventory_model import Items, Inventory
from models.users_model import Quests
from models.marketplace_model import ShopDaily,Marketplace



from services.exp_services import current_exp
from services.inventory_services import fetch_inventory, take_item, calculate_slots_used
from services.users_services import update_longest_quest_streak
from services.economy_services import remove_gold

from utils.embeds.delieveryembed import delievery_embed
from utils.itemname_to_id import get_item_id_safe
from utils.custom_errors import NotEnoughGoldError
from utils.emotes import GOLD_EMOJI

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
        rerolls = quest.rerolls if quest else 0
        gold_needed = REROLL_COST.get(rerolls, 500)

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
        gold_needed
    )
    return embed


def create_quest(user_id: int, reset_rerolls: bool = False):
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
        invenotry_slots_used_by_user = calculate_slots_used(user_id, session)
        num_items = number_of_items_for_quest(invenotry_slots_used_by_user)

        delivery_items = (
            session.execute(
                select(Items)
                .where(
                    Items.item_rarity.in_(rarity_pool),
                    Items.item_usable.is_(False)
                )
                .order_by(func.random())
                .limit(num_items)
            )
            .scalars()
            .all()
        )

        reward = calculate_reward(delivery_items, user_id)

        # decide max quantity per item based on user level
        max_qty = quantity_for_level(user_lvl)

        # gacha roll per item: 1 -> max_qty
        delivery_items_dict = {
            item.item_name: random.randint(1, max_qty)
            for item in delivery_items
        }

        existing_quest = session.execute(
            select(Quests).where(Quests.user_id == user_id)
        ).scalar_one_or_none()

        if existing_quest:
            existing_quest.delivery_items = delivery_items_dict
            existing_quest.reward = reward
            existing_quest.limit += 1
        else:
            session.add(
                Quests(
                    user_id=user_id,
                    delivery_items=delivery_items_dict,
                    reward=reward,
                    limit=0,
                    skips=0,
                    rerolls=0,
                )
            )
        if reset_rerolls:
            if existing_quest:
                existing_quest.rerolls = 0

        session.commit()

    logger.info(
        "Quest created",
        extra={
            "user": user_id,
            "flex": f"Items requested -> {delivery_items_dict}, Reward -> {reward}",
        },
    )

    return delivery_items_dict, reward


def delete_quest(user_id: int, streak: bool = False, skip: bool = True):
    """
    Skips (deletes) the current quest for the user.

    Rules:
    - User can only skip if skip limit allows
    - Skipping resets items and reward
    - Streak is reset unless explicitly preserved
    - Skip is increased unless explicitly preserved

    Returns:
        bool: True if skipped successfully, False otherwise
    """
    with Session() as session:
        quest = session.execute(
            select(Quests).where(Quests.user_id == user_id)
        ).scalar_one_or_none()

        if skip and not can_skip(quest.skips):
            return False

        quest.delivery_items = None
        quest.reward = 0

        if skip:
            quest.skips += 1

        if not streak:
            quest.streak = 0

        session.commit()

    logger.info("Quest skipped", extra={"user": user_id})
    return True

def reroll_quest(user_id: int):
    with Session() as session:
        quest = session.get(Quests, user_id)

        if not quest:
            # no quest exists yet, just generate one SHOULD NVR RUN IDK WHY I ADDED THIS
            create_quest(user_id)
            return "You didn’t even have a quest I made you one. Use `/quest`."

        rerolls_used = quest.rerolls
        gold_needed = REROLL_COST.get(rerolls_used, 500)

        try:
            remove_gold(user_id, gold_needed, session)
        except NotEnoughGoldError:
            return f"You don't have {gold_needed}{GOLD_EMOJI} to reroll."

        # increment reroll count
        quest.rerolls += 1
        session.commit()

    # refresh quest contents (preserve streak, don't count skip)
    delete_quest(user_id, streak=True, skip=False)
    create_quest(user_id)

    return "Okeyyyy I'll see if I need something else from you. Use `/quest` again!"

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
    Calculate delivery reward based on item rarities, quantities, and streak.
    """

    # fetch quest to read quantities
    with Session() as session:
        quest = session.execute(
            select(Quests).where(Quests.user_id == user_id)
        ).scalar_one_or_none()
        streak = quest.streak if quest else 0
        quantities = quest.delivery_items if quest and quest.delivery_items else {}

    rarities_list = []

    # expand rarities by quantity
    for item in items:
        qty = quantities.get(item.item_name, 1)
        rarities_list.extend([item.item_rarity] * qty)

    return final_delivery_reward(rarities_list, streak)


def items_check(user_id: int, items: dict):
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

    # items is expected to be dict{name: amount}
    for item_name, amount in items.items():
        if item_name not in owned_items:
            return False

        for inv_item in inventory:
            if inv_item["item_name"] == item_name and inv_item["item_quantity"] < amount:
                return False

    # removal
    for item_name, amount in items.items():
        item_id, _ = get_item_id_safe(item_name)
        take_item(user_id, item_id, amount)

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
        new_streak = quest.streak
        session.commit()

    # update stats in a separate transaction
    update_longest_quest_streak(user_id, new_streak)

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



def lookup_item_sources(user_id: int, item_name: str):
    """
    Returns info about where an item can be found.

    Output example:
    {
        "shop": True/False,
        "marketplace": [listing_ids],
        "players": [user_ids],
        "message": str
    }
    """

    SPY_COST = 25

    # Resolve item name using fuzzy-safe util
    item_id, suggestions = get_item_id_safe(item_name)

    try:
        with Session() as session:
            remove_gold(user_id, SPY_COST, session)
            session.commit()

    except NotEnoughGoldError:
        return {
            "shop": False,
            "marketplace": [],
            "players": [],
            "message": f"🕵️ I ain't running errands for free. Come back with 25 {GOLD_EMOJI}."
        }

    if item_id is None:
        return {
            "shop": False,
            "marketplace": [],
            "players": [],
            "message": (
                "❌ Item not recognized.\n"
                + ("Did you mean: " + ", ".join(suggestions) if suggestions else "")
            )
        }

    result = {
        "shop": False,
        "marketplace": [],
        "players": [],
        "message": ""
    }

    with Session() as session:

        # --- Shop ---
        latest_date = session.execute(
            select(func.max(ShopDaily.date))
        ).scalar()

        shop_item = session.execute(
            select(ShopDaily)
            .where(
                ShopDaily.item_id == item_id,
                ShopDaily.date == latest_date,
                ShopDaily.shop_type == "sell"
            )
        ).scalars().first()

        if shop_item:
            result["shop"] = True

        # --- Marketplace (limit 3) ---
        mp_items = session.execute(
            select(Marketplace)
            .where(Marketplace.item_id == item_id)
            .limit(3)
        ).scalars().all()

        result["marketplace"] = [m.listing_id for m in mp_items]

        # --- Player inventories (limit 3) ---
        owners = session.execute(
            select(Inventory.user_id)
            .distinct()
            .where(
                Inventory.item_id == item_id,
                Inventory.item_quantity > 0
            )
            .limit(3)
        ).scalars().all()

        result["players"] = owners

    # ---------- Build message ----------
    lines = []

    if result["shop"]:
        lines.append("🏪 Available in Daily Shop. Check out `/shop`")

    if result["marketplace"]:
        ids = ", ".join(str(i) for i in result["marketplace"])
        lines.append(f"🛒 Spotted on the marketplace (listing IDs: {ids}).")

    if result["players"]:
        mentions = ", ".join(f"<@{u}>" for u in result["players"])
        lines.append(f"👤 Rumor says these players own atleast one: {mentions}")

    if not lines:
        lines.append(
            "❌ No leads found.\n"
            "Try waiting for a shop reroll, opening boxes, or running explorer jobs and praying to RNGesus."
        )

    result["message"] = "\n".join(lines)

    return result