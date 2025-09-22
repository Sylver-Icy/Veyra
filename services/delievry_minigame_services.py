from sqlalchemy import select, func, delete
import random
from models.inventory_model import Items
from models.users_model import Quests
from database.sessionmaker import Session
from utils.embeds.delieveryembed import delievery_embed
from utils.itemname_to_id import get_item_id_safe
from services.inventory_services import fetch_inventory, take_item

def requested_items(user_name: str, user_id: int):
    """
    Checks if user has already assigned quest
    Send the quest is already assigne else create a new then send
    TODO: make it scale with user lvl
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
    Creates a delievery quest
    Picks 1,2 random items from table
    Adds the new quest to db
    """
    with Session() as session:
        delivery_items = session.execute(
            select(Items)
            .where(Items.item_rarity == "Common")
            .order_by(func.random())
            .limit(random.randint(1,2))
        ).scalars().all()  #pick 1/2 random common items from table
        reward = calculate_reward(delivery_items) #get the reward for quest based on items picked
        delivery_items_name_list = [item.item_name for item in delivery_items] # Convert ORM items to string names for JSON storage
        new_quest = Quests(
            user_id = user_id,
            delivery_items = delivery_items_name_list,
            reward = reward,
            limit =1
        ) #add the newly made quest
        session.add(new_quest)
        session.commit()
    return delivery_items_name_list,reward
def delete_quest(user_id: int):
    with Session() as session:
        session.execute(
            delete(Quests)
            .where(Quests.user_id == user_id)
            )
        session.commit()

def fetch_quest(user_id: int):
    """
    Fetches already existing quest return none if there is no quest
    """
    with Session() as session:
        return session.execute(
            select(Quests)
            .where(Quests.user_id == user_id)
        ).scalar_one_or_none()


def calculate_reward(items: list):
    """
    Calculates the reward for deilevry quest
    """
    RARITY_REWARDS = {
        "Common": (10,15),
        "Rare": (25,32),
        "Epic": (71,93),
        "Legendary": (181,321),
        "Paragon": (799,1211)
    }
    total = 0
    for item in items:
        low,high = RARITY_REWARDS.get(item.item_rarity)
        total += random.randint(low,high)
    bonus = round(random.uniform(1.1,1.7),2)
    return int(total*bonus)

def items_check(user_id: int, items: list):
    """
    checks if user has the items in inventory for delievry
    if user has item deductes them
    """
    inventory = fetch_inventory(user_id)
    # set of names of all items owner by user with each having => 1 quantity
    items_set = {item["item_name"] for item in inventory if item["item_quantity"]>0}
    for item in items:
        if item not in items_set:
            return False #return false if any of the required items are missing
    for item in items:
        item_id,a = get_item_id_safe(item) #placeholder 'a' coz this func returns item_name and suggestions
        take_item(user_id, item_id, 1)
    return True
