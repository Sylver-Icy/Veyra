from sqlalchemy.sql import func
from database.sessionmaker import Session
from models.inventory_model import Items
from utils.embeds.shopembed import shop_embed
from services.inventory_services import give_item
from services.economy_services import remove_gold, check_wallet
daily_shop_items =[] #List to store items in shop for current day
def update_daily_shop():
    """
    Updates the shop with new items. 5items are randomly selected from all items in database
    """
    global daily_shop_items
    with Session() as session:
        random_items = session.query(Items).order_by(func.random()).limit(6).all()
        daily_shop_items = [
            {
            "name": item.item_name,
            "id": item.item_id,
            "price": item.item_price,
            "description": item.item_description,
            "rarity": item.item_rarity
            }
            for item in random_items
        ]

def daily_shop():
   return shop_embed(daily_shop_items)

def buy_item(user_id, item_id, item_quantity):
    item_id = int(item_id)
    if item_quantity <= 0:
        print("Invalid quantity")
        return "Invalid quantity"

    if item_id not in [item["id"] for item in daily_shop_items]:
        print("Wrong item")
        return "Item not in shop"

    item_price = next(item["price"] for item in daily_shop_items if item["id"] == item_id)
    user_gold = check_wallet(user_id)
    if user_gold < item_price * item_quantity:
        print("No gold")
        return "Not enough gold"

    give_item(user_id, item_id, item_quantity)
    remove_gold(user_id, item_price * item_quantity)
    return "Purchase successful"
    



from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()
scheduler.add_job(update_daily_shop, 'interval', minutes=24)
