import random
from sqlalchemy.sql import func
from database.sessionmaker import Session
from models.inventory_model import Items
from utils.embeds.shopembed import get_shop_view_and_embed
from utils.emotes import GOLD_EMOJI
from services.inventory_services import give_item, take_item, fetch_inventory
from services.economy_services import remove_gold, add_gold, check_wallet

daily_shop_items = [] #List to store items in shop for current day
def update_daily_shop():
    with Session() as session:
        random_items = session.query(Items).order_by(func.random()).limit(6).all()

        # clear the list and refill it
        daily_shop_items.clear()
        daily_shop_items.extend([
            {
                "name": item.item_name,
                "id": item.item_id,
                "price": item.item_price,
                "description": item.item_description,
                "rarity": item.item_rarity
            }
            for item in random_items
        ])

daily_buyback_shop_items = [] #List to store items bot is gonna be buying
def update_daily_buyback_shop():
    with Session() as session:
        random_items = (
            session.query(Items)
            .where(Items.item_rarity.in_(("Common", "Rare", "Epic", "Legendary")))
            .order_by(func.random())
            .limit(4)
            .all()
        )
        daily_buyback_shop_items.clear()
        daily_buyback_shop_items.extend([
    {
        "name": item.item_name,
        "id": item.item_id,
        "description": item.item_description,
        "price": calculate_buy_price(item.item_rarity, bonus=(i == 3))  # bonus only for 4th item
    }
    for i, item in enumerate(random_items)
    ])

def calculate_buy_price(rarity: str, bonus: bool):
    """
    Dynamically calculates the price at which bot will be buying items based on rarity
    Applies bonus in certain cases
    """
    BUY_PRICE = {
        "Common": (7,10),
        "Rare": (17,20),
        "Epic": (59,65),
        "Legendary": (250,300),
        "Paragon": (500,600)
    }
    if bonus:
        low,high = BUY_PRICE.get(rarity,(0,0)) # select the lowest and highest possible price from dic
        price = random.randint(low, high) # randomly select the price for current item
        bonus_multiplier = random.uniform(1.3,2.2) #calucate a random multiplier for inflate the price of item
        return int(price*bonus_multiplier)
    else:
        low,high = BUY_PRICE.get(rarity,(0,0))
        return random.randint(low,high)

def daily_shop():
   """Returns today's shop"""
   return get_shop_view_and_embed(daily_shop_items, daily_buyback_shop_items)

def buy_item(user_id, item_id, item_quantity):
    """
    Handles purchasing an item from the shop.

    Parameters:
    - user_id (int): The ID of the user making the purchase.
    - item_id (int): The ID of the item to buy.
    - item_quantity (int): The quantity of the item to buy.

    Returns:
    - str: A message indicating the result of the purchase attempt.
    """

    # Validate that user wants to buy at least one item
    if item_quantity <= 0:
        return "Its not funny ._."

    # Check if the item exists in the current daily shop
    if item_id not in [item["id"] for item in daily_shop_items]:
        return "That item is not currently in shop use /shop to look available items"

    # Get the price of the item
    item_price = next(item["price"] for item in daily_shop_items if item["id"] == item_id)

    # Check if the user has enough gold to buy the desired quantity
    user_gold = check_wallet(user_id)
    if user_gold < item_price * item_quantity:
        if user_gold < item_price:
            return "Nuh uh! TOOO BROKE BRUH. Next time check your wallet before coming here 🔪"
        # Suggest the max quantity user can afford
        return f"You can't buy that many... HOWEVERRRR you can get `{user_gold // item_price}` of it"

    # Give the item to the user and deduct the gold
    give_item(user_id, item_id, item_quantity)
    remove_gold(user_id, item_price * item_quantity)

    return "Purchase successful"


def sell_item(user_id: int, item_id: int, item_quantity: int):
    """
    Handles selling an item back to the buyback shop.

    Parameters:
    - user_id (int): The ID of the user selling the item.
    - item_id (int): The ID of the item to sell.
    - item_quantity (int): The quantity of the item to sell.

    Returns:
    - str: A message indicating the result of the sell attempt.
    """

    # Validate that user wants to sell at least one item
    if item_quantity <= 0:
        return "You need to sell atleast 1 bruh"

    # Check if the item is currently wanted by the buyback shop
    if item_id not in [item["id"] for item in daily_buyback_shop_items]:
        return "I don't need that right now, use `/shop` to see items I need today"

    # Fetch the user's inventory and find how many of the item they own
    inventory = fetch_inventory(user_id)
    item_quantity_owned_by_user = next(
        (item["item_quantity"] for item in inventory if item["item_id"] == item_id),
        0  # default if not found
    )

    # Check if user has enough quantity to sell
    if item_quantity_owned_by_user < item_quantity:
        if item_quantity_owned_by_user == 0:
            return "What are you tryna sell? your soul?"
        else:
            return f"You have only {item_quantity_owned_by_user}... How were you planning to sell me {item_quantity}?"

    # Get the price at which the buyback shop will buy the item
    item_price = next((item["price"] for item in daily_buyback_shop_items if item["id"] == item_id), 0)

    # Remove the item from user's inventory and add gold
    take_item(user_id, item_id, item_quantity)
    add_gold(user_id, (item_price * item_quantity))

    return (
        f"Great doing bussiness with you, I transferred you your {item_price * item_quantity} {GOLD_EMOJI},\n"
        "You can check with `!checkwallet` :3"
    )
