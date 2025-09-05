from sqlalchemy.sql.expression import func
from models.inventory_model import Items, Inventory
from database.sessionmaker import Session
from utils.itemname_to_id import item_name_to_id
import random

#All the boxes with their respective rewards distribution
wooden_box_rarities = {"Gold": 91, "Common": 8, "Rare": 0.9, "Epic": 0.1}
stone_box_rarities = {"Gold": 78, "Common": 20, "Rare": 1.9, "Epic": 0.1}
iron_box_rarities = {"Gold": 62, "Common": 29, "Rare": 8.5, "Epic": 0.5}
platinum_box_rarities = {"Gold": 51, "Common": 30, "Rare": 18, "Epic": 0.9,"Legendary": 0.1}

LOOTBOX_CONFIGS = {
    "Wooden Box": wooden_box_rarities,
    "Stone Box": stone_box_rarities,
    "Iron Box": iron_box_rarities,
    "Platinum Box": platinum_box_rarities
}


def lootbox_reward(lootbox: str):
    """
    Calculates the reward of any box
    Take the box dic then assign weight to items according to weight in dic to calculate reward
    """
    rarity_dic = LOOTBOX_CONFIGS.get(lootbox.title())
    result = random.choices(
        population=list(rarity_dic.keys()),
        weights=list(rarity_dic.values()),
        k=1
    )[0] #Choosing what does player gets item or gold

    if result == "Gold": #if reward is gold then calculate the gold amount
        return {"Gold": decide_gold(lootbox.title())}
    else: #else pick random item of rewarded rarity
        return {"Item": pick_random_item(result),"Rarity": result}

def pick_random_item(rarity: str):
    """
    Uses sqlalchemy's fucn to pick random item of set rarirty from items table
    """
    with Session() as session:
        item = session.query(Items).filter_by(item_rarity=rarity).order_by(func.random()).first() # pylint: disable=not-callable
        return item.item_name

def decide_gold(lootbox:str):
    """
    Takes name of lootbox as input then rewards gold based on that
    """
    if lootbox == "Wooden Box":
        return random.randint(3,12)
    if lootbox == "Stone Box":
        return random.randint(11,22)
    if lootbox == "Iron Box":
        return random.randint(65,110)
    if lootbox == "Platinum Box":
        return random.randint(200,500)

def user_lootbox_count(user_id: int,lootbox_name: str):
    """
    Queries the database to check how many of the required lootbox user has
    """
    item_id = item_name_to_id.get(lootbox_name.lower())
    if item_id is None:
        return -1
    with Session() as session:
        lootbox = session.query(Inventory).filter_by(
            user_id = user_id,
            item_id = item_id
            ).first()
        return lootbox.item_quantity if lootbox else 0
