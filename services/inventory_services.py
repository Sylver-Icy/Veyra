"""This module handles inventory-related services like adding items and assigning them to users."""
import logging
import discord
from typing import Tuple, Optional, List
from database.sessionmaker import Session
from models.inventory_model import Inventory, Items
from models.users_model import User
from utils.custom_errors import UserNotFoundError, NotEnoughItemError, InvalidItemAmountError
from utils.itemname_to_id import item_name_to_id
from utils.embeds.inventoryembed import build_inventory, build_item_info_embed
from services.users_services import is_user

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
    if not is_user(target_id):
        raise UserNotFoundError(target_id)

    if amount < 1:
        raise InvalidItemAmountError

    with Session() as session:
        entry = session.get(Inventory, (target_id, item_id))

        # check if item exists in db
        # if not item:
        #     raise WrongItemError()
        if entry: #If user already have the item
            entry.item_quantity += amount
        else:
            new_entry = Inventory(
                user_id=target_id,
                item_id=item_id,
                item_quantity=amount,
            )
            session.add(new_entry)

        session.commit()

def take_item(target_id: int, item_id: int, amount: int):
    """
    Removes specified amount of item from target
    """
    if not is_user(target_id):
        raise UserNotFoundError(target_id)

    if amount < 1:
        raise InvalidItemAmountError

    with Session() as session:
        entry = session.get(Inventory, (target_id,item_id))

        if not entry or entry.item_quantity < amount:
            raise NotEnoughItemError

        entry.item_quantity -= amount

        #delete row is it reaches 0
        if entry.item_quantity == 0:
            session.delete(entry)

        session.commit()

def transfer_item(sender_id: int, receiver_id: int, item_id: int, amount:int):
    """
    Transfers given amount of given item from sender to reciver
    """
    if not is_user(sender_id):
        raise UserNotFoundError(sender_id)
    if not is_user(receiver_id):
        raise UserNotFoundError(receiver_id)
    if amount < 1:
        raise InvalidItemAmountError

    with Session() as session:
        entry1 = session.get(Inventory,(sender_id,item_id)) #Sender's row
        entry2 = session.get(Inventory,(receiver_id,item_id)) #reciver's row

        #raise an error is sender has insuffiecient items to send
        if not entry1 or entry1.item_quantity<amount:
            raise NotEnoughItemError

        entry1.item_quantity -= amount #deduct the amount for transaction

        #if sender has no more items left delete the row
        if entry1.item_quantity == 0:
            session.delete(entry1)

        if entry2: #if reciver already has the item
            entry2.item_quantity += amount
        else: #if reciver has no such item
            new_entry = Inventory(
                user_id=receiver_id,
                item_id=item_id,
                item_quantity=amount,
            )
            session.add(new_entry)
        session.commit()

def fetch_inventory(user_id: int) -> List[dict]:
    """Returns a list of items in user's inventory (excluding zero quantity)."""
    with Session() as session:
        inventory = session.query(Inventory).filter_by(user_id=user_id).all()
        result = []

        for entry in inventory:
            if entry.item_quantity < 1:
                continue
            item = session.get(Items, entry.item_id)
            result.append({
                "item_id": entry.item_id,
                "item_name": item.item_name,
                "item_quantity": entry.item_quantity,
                "item_rarity": item.item_rarity,
                "item_description": item.item_description
            })

        return result

def get_inventory(user_id: int, user_name: str) -> Tuple[Optional[str], Optional[discord.Embed]]:
    """
    Returns an embed of items owned by user
    If user has no items it triggers the starter event
    If starter event already done then skip
    """
    with Session() as session:
        user = session.get(User, user_id)
        result = fetch_inventory(user_id)

        if not result:
            if user.starter_given:
                embed_pages = build_inventory(user_name, result)
                return (None, embed_pages)
            else:
                give_item(user_id, 2, 1)
                user.starter_given = True
                session.commit()
                return ("start_event", None)
        else:
            return (None, build_inventory(user_name, result))

def get_item_details(item_id: int):
    item_details = {}
    with Session() as session:
        item = session.get(Items, item_id)
        item_details['name'] = item.item_name
        item_details['description'] = item.item_description
        item_details['rarity'] = item.item_rarity
        item_details['icon'] = item.item_icon
    return build_item_info_embed(item_details)