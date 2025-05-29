from database.sessionmaker import Session
from models.inventory_model import Inventory, Items
from utils.custom_errors import WrongItemError
import logging

logger = logging.getLogger('__name__')

def add_item(
    item_id: int,
    item_name: str,
    item_description: str,
    item_rarity: str,
    item_icon: str = None,
    item_durability: str = None
):
    """Adds an item to database"""
    with Session() as session:
        item_by_id = session.get(Items, item_id)
        item_by_name = session.query(Items).filter_by(item_name=item_name).first()

        if item_by_id or item_by_name:
            return True
        
        new_item = Items(
            item_id = item_id,
            item_name = item_name,
            item_description = item_description,
            item_rarity = item_rarity,
            item_icon = item_icon,
            item_durability = item_durability

        )
        session.add(new_item)
        session.commit()

def give_item(user_id: int, item_id: int, amount: int):
    """Gives any item to any user"""
    with Session() as session:
        entry = session.get(Inventory, (user_id, item_id))
        item = session.get(Items, item_id)
        if not item:
            raise WrongItemError()
        if entry: #If user already have the item
            entry.item_quantity += amount
        else:
            new_entry = Inventory(
                user_id=user_id,
                item_id=item_id,
                item_quantity=amount,
                item_durability=item.item_durability
            )
            session.add(new_entry)

        session.commit()