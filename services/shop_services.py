import logging
import random
from sqlalchemy.sql import func

from database.sessionmaker import Session
from models.inventory_model import Items
from utils.embeds.shopembed import get_shop_view_and_embed
from utils.emotes import GOLD_EMOJI
from services.inventory_services import give_item, take_item, fetch_inventory
from services.economy_services import remove_gold, add_gold, check_wallet

logger = logging.getLogger(__name__)

# List to store items available in the shop for the current day
daily_shop_items = []

# List to store items the bot will buy back today
daily_buyback_shop_items = []

ITEM_RATE = {
    "Common": (5, 10),
    "Rare": (15, 25),
    "Epic": (50, 80),
    "Legendary": (200, 300),
    "Paragon": (600, 900)
}

def update_daily_shop():
    """
    Updates the daily shop with 6 random items from the database.
    """
    with Session() as session:
        random_items = (
            session.query(Items)
            .where(Items.item_rarity.in_(("Common", "Rare", "Epic", "Legendary")))
            .order_by(func.random())
            .limit(9)
            .all()
        )

        daily_shop_items.clear()
        daily_shop_items.extend([
            {
                "name": item.item_name,
                "id": item.item_id,
                "price": calculate_buy_price(item.item_rarity,False),
                "description": item.item_description,
                "rarity": item.item_rarity
            }
            for item in random_items
        ])

    logger.info("Daily shop updated")


def update_daily_buyback_shop():
    """
    Updates the daily buyback shop with 4 random items of certain rarities.
    Ensures no overlap with today's shop.
    The 4th item gets a bonus price multiplier.
    """
    with Session() as session:
        # Collect all item IDs currently in daily shop
        excluded_ids = [item["id"] for item in daily_shop_items]

        # Fetch random items excluding those in daily shop
        random_items = (
            session.query(Items)
            .where(Items.item_rarity.in_(("Common", "Rare", "Epic", "Legendary")))
            .where(~Items.item_id.in_(excluded_ids))
            .order_by(func.random())
            .limit(6)
            .all()
        )

        daily_buyback_shop_items.clear()
        daily_buyback_shop_items.extend([
            {
                "name": item.item_name,
                "id": item.item_id,
                "description": item.item_description,
                "price": calculate_buy_price(item.item_rarity, bonus=(i == 5))  # Bonus for 6th item
            }
            for i, item in enumerate(random_items)
        ])

    logger.info("Daily buyback shop updated (no overlap with daily shop)")


def calculate_buy_price(rarity: str, bonus: bool) -> int:
    """
    Dynamically calculates the price at which the bot will buy items, based on rarity.

    Parameters:
    - rarity (str): The rarity level of the item.
    - bonus (bool): Whether to apply a bonus multiplier to the price.

    Returns:
    - int: The calculated price.
    """
    low, high = ITEM_RATE.get(rarity, (0, 0))

    if bonus:
        price = random.randint(low, high)
        bonus_multiplier = random.uniform(1.3, 2.2)
        return int(price * bonus_multiplier)
    else:
        return random.randint(low, high)


def daily_shop():
    """
    Returns the shop view and embed for today's shop items.

    Returns:
    - Tuple[discord.Embed, discord.ui.View]: The visual representation of the shop.
    """
    return get_shop_view_and_embed(daily_shop_items, daily_buyback_shop_items)


def buy_item(user_id: int, item_id: int, item_quantity: int) -> str:
    """
    Handles purchasing an item from the shop.

    Parameters:
    - user_id (int): The ID of the user making the purchase.
    - item_id (int): The ID of the item to buy.
    - item_quantity (int): The quantity of the item to buy.

    Returns:
    - str: A message indicating the result of the purchase attempt.
    """
    if item_quantity <= 0:
        return "Its not funny ._."

    # Check if the item exists in the current daily shop
    if item_id not in [item["id"] for item in daily_shop_items]:
        return "That item is not currently in shop. Use `/shop` to see available items."

    # Get the price of the item
    item_price = next(item["price"] for item in daily_shop_items if item["id"] == item_id)

    # Check if the user has enough gold
    user_gold = check_wallet(user_id)
    total_cost = item_price * item_quantity

    if user_gold < total_cost:
        if user_gold < item_price:
            return "Nuh uh! TOO BROKE BRUH. Next time check your wallet before coming here 🔪"
        return f"You can't buy that many... HOWEVER, you can get `{user_gold // item_price}` of it."

    # Process purchase
    give_item(user_id, item_id, item_quantity)
    remove_gold(user_id, total_cost)

    return "Purchase successful"


def sell_item(user_id: int, item_id: int, item_quantity: int) -> str:
    """
    Handles selling an item back to the buyback shop.

    Parameters:
    - user_id (int): The ID of the user selling the item.
    - item_id (int): The ID of the item to sell.
    - item_quantity (int): The quantity of the item to sell.

    Returns:
    - str: A message indicating the result of the sell attempt.
    """
    if item_quantity <= 0:
        return "You need to sell at least 1 bruh."

    # Check if the item is wanted by the buyback shop
    if item_id not in [item["id"] for item in daily_buyback_shop_items]:
        return "I don't need that right now. Use `/shop` to see items I need today."

    # Check user's inventory for the item
    inventory = fetch_inventory(user_id)
    item_quantity_owned = next(
        (item["item_quantity"] for item in inventory if item["item_id"] == item_id),
        0
    )

    if item_quantity_owned < item_quantity:
        if item_quantity_owned == 0:
            return "What are you tryna sell? Your soul?"
        return f"You have only {item_quantity_owned}... How were you planning to sell me {item_quantity}?"

    # Get item price
    item_price = next((item["price"] for item in daily_buyback_shop_items if item["id"] == item_id), 0)
    total_gold = item_price * item_quantity

    # Process sale
    take_item(user_id, item_id, item_quantity)
    add_gold(user_id, total_gold)

    logger.info("Items sold to Veyra", extra={
        "user": user_id,
        "flex": f"Item sold -> {item_id} at rate of -> {item_price} | Quantity -> {item_quantity}"
    })

    return (
        f"Great doing business with you! I transferred your {total_gold} {GOLD_EMOJI}.\n"
        "You can check with `!checkwallet` :3"
    )
