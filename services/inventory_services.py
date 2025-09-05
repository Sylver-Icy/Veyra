"""This module handles inventory-related services like adding items and assigning them to users."""
import logging
import discord
from database.sessionmaker import Session
from models.inventory_model import Inventory, Items
from utils.custom_errors import WrongItemError
from utils.itemname_to_id import item_name_to_id
from utils.embeds.inventoryembed import build_inventory

logger = logging.getLogger('__name__')

def add_item(
    item_id: int,
    item_name: str,
    item_description: str,
    item_price: int,
    item_rarity: str,
    item_icon: str = None,
    item_durability: int = None
):
    """Adds an item to database"""
    with Session() as session:
        item_by_id = session.get(Items, item_id)
        item_by_name = session.query(Items).filter_by(item_name=item_name).first()

        if item_by_id or item_by_name:
            return True
        new_item = Items(
            item_id = item_id,
            item_name = item_name.title(),
            item_description = item_description,
            item_rarity = item_rarity,
            item_icon = item_icon,
            item_durability = item_durability,
            item_price = item_price

        )
        session.add(new_item)
        item_name_to_id[item_name] = item_id
        session.commit()

def give_item(target_id: int, item_id: int, amount: int):
    """Gives any item to any user"""
    with Session() as session:
        entry = session.get(Inventory, (target_id, item_id))
        item = session.get(Items, item_id)
        if not item:
            raise WrongItemError()
        if entry: #If user already have the item
            entry.item_quantity += amount
        else:
            new_entry = Inventory(
                user_id=target_id,
                item_id=item_id,
                item_quantity=amount,
                item_durability=item.item_durability
            )
            session.add(new_entry)

        session.commit()



def get_inventory(user_id: int, user_name: str) -> discord.Embed:
    """
    Fetches all items a user owns and turn them in a list of dicts,
    and calls embed builder to return an embed
    """
    with Session() as session:
        inventory = session.query(Inventory).filter_by(user_id=user_id).all()
        result = []
        for entry in inventory:
            if entry.item_quantity == 0:
                continue
            item = session.get(Items, entry.item_id)
            result.append({
                "item_id": entry.item_id,
                "item_name": item.item_name,
                "item_quantity": entry.item_quantity,
                "item_rarity": item.item_rarity,
                "item_description": item.item_description
            })
        if result:
            return build_inventory(user_name,result)
        return ("You dont have anything") 