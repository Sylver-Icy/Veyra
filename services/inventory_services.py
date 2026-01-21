"""This module handles inventory-related services like adding items and assigning them to users."""
import logging
import math

import discord

from typing import Tuple, Optional, List
from database.sessionmaker import Session

from models.inventory_model import Inventory, Items
from models.users_model import User, Upgrades

from domain.inventory.rules import available_inventory_slots_for_user, allowed_stack_size

from services.users_services import is_user

from utils.custom_errors import UserNotFoundError, NotEnoughItemError, InvalidItemAmountError, FullInventoryError, PartialInventoryError
from utils.embeds.inventoryembed import build_inventory, build_item_info_embed
from utils.usable_items import UsableItemHandler


logger = logging.getLogger('__name__')


def give_item(target_id: int, item_id: int, amount: int, overflow: bool = False):
    """Gives any item to any user"""

    if amount < 1:
        raise InvalidItemAmountError

    with Session() as session:
        if not is_user(target_id, session):
            raise UserNotFoundError(target_id)

        user = session.get(User, target_id)
        if not user:
            raise UserNotFoundError(target_id)

        if not overflow:
            allowed = max_addable_amount(target_id, item_id, session)

            if allowed == 0:
                raise FullInventoryError()

            if allowed < amount:
                item = session.get(Items, item_id)
                item_name = item.item_name if item else None
                raise PartialInventoryError(requested=amount, allowed=allowed, item_name=item_name)

        entry = session.get(Inventory, (target_id, item_id))

        if entry: #If user already have the item
            entry.item_quantity += amount
        else:
            new_entry = Inventory(
                user_id=target_id,
                item_id=item_id,
                item_quantity=amount,
            )
            session.add(new_entry)
        if overflow:
            logger.warning(
                "SYSTEM GRANT (overflow=True): user=%s item=%s amount=%s",
                target_id, item_id, amount
            )

        session.commit()

def take_item(target_id: int, item_id: int, amount: int):
    """
    Removes specified amount of item from target
    """

    if amount < 1:
        raise InvalidItemAmountError

    with Session() as session:
        if not is_user(target_id, session):
            raise UserNotFoundError(target_id)

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

    if amount < 1:
        raise InvalidItemAmountError

    with Session() as session:
        if not is_user(sender_id, session):
            raise UserNotFoundError(sender_id)
        if not is_user(receiver_id, session):
            raise UserNotFoundError(receiver_id)

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
        inventory = (
            session.query(Inventory, Items)
            .join(Items, Inventory.item_id == Items.item_id)
            .filter(Inventory.user_id == user_id)
            .order_by(Items.item_name.asc())
            .all()
            )

    result = []
    for entry, item in inventory:
        if entry.item_quantity < 1:
            continue
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
                give_item(user_id, 164, 1)
                user.starter_given = True
                session.commit()
                return ("start_event", None)
        else:
            return (None, build_inventory(user_name, result))

def get_item_details(user_id, item_id: int):
    item_details = {}
    with Session() as session:
        item = session.get(Items, item_id)
        user_inv = session.get(Inventory, (user_id, item_id))
        if not item:
            return None
        item_details['name'] = item.item_name
        item_details['description'] = item.item_description
        item_details['rarity'] = item.item_rarity
        item_details['icon'] = item.item_icon
        item_details['amount_owned'] = user_inv.item_quantity
    return build_item_info_embed(item_details)

def use_item(user_id: int, item_id: str):
    with Session() as session:
        item = session.get(Items, item_id)
        if not item:
            return "That item doesn't exist."
        if not item.item_usable:
            return f"{item.item_name} can’t be used."

        handler = UsableItemHandler.get_handler(item.item_name)
        if not handler:
            return f"{item.item_name} is marked as usable but has no handler (dev issue)."

        # Remove the item before use
        try:
            take_item(user_id, item.item_id, 1)
             # Run item logic
            result = handler(user_id)

        except NotEnoughItemError:
            return(f"You don't have any {item.item_name} left. Buy or trade some to use it.")
        return result


def calculate_slots_used(user_id: int, session) -> int:
    """
    Returns how many inventory slots the user is currently using.
    Each item consumes ceil(quantity / stack_limit) slots.
    """
    # get user upgrades once
    user_pockets = session.get(Upgrades, (user_id, "pockets"))

    # fetch inventory joined with items for rarity
    rows = (
        session.query(Inventory.item_id, Inventory.item_quantity, Items.item_rarity)
        .join(Items, Inventory.item_id == Items.item_id)
        .filter(Inventory.user_id == user_id)
        .all()
    )

    total_slots_used = 0

    for item_id, qty, rarity in rows:
        if qty <= 0:
            continue

        stack_limit = allowed_stack_size(user_pockets.level, rarity)
        if stack_limit < 1:
            print(f"Invalid stack_limit={stack_limit} for rarity={rarity}, pockets={user_pockets.level}")

        stacks_needed = math.ceil(qty / stack_limit)

        total_slots_used += stacks_needed

    return total_slots_used


def max_addable_amount(user_id: int, item_id: int, session) -> int:
    """
    Returns the maximum amount of item_id that can be added right now,
    given inventory slot + stacking constraints.
    """
    user_inv = session.get(Upgrades, (user_id, "inventory"))
    user_pockets = session.get(Upgrades, (user_id, "pockets"))

    item = session.get(Items, item_id)
    if not item:
        return 0

    stack_limit = allowed_stack_size(user_pockets.level, item.item_rarity)
    slots_allowed = available_inventory_slots_for_user(user_inv.level)

    slots_used_now = calculate_slots_used(user_id, session)
    free_slots = max(0, slots_allowed - slots_used_now)

    entry = session.get(Inventory, (user_id, item_id))
    current_qty = entry.item_quantity if entry else 0

    # If user doesn't already have the item, they need at least 1 slot to add any
    if current_qty == 0:
        return free_slots * stack_limit

    # User already has this item -> can fill current partial stack without new slots
    remainder = current_qty % stack_limit
    room_in_current_stack = (stack_limit - remainder) if remainder != 0 else 0

    return room_in_current_stack + (free_slots * stack_limit)


def allow_item_in_inventory(user_id: int, item_id: int, amount: int, session) -> bool:
    return max_addable_amount(user_id, item_id, session) >= amount