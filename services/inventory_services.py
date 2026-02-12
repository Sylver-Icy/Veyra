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


logger = logging.getLogger(__name__)


def give_item(target_id: int, item_id: int, amount: int, overflow: bool = False, session=None):
    """Gives any item to any user"""

    if amount < 1:
        raise InvalidItemAmountError

    owns_session = False
    if session is None:
        session = Session()
        owns_session = True

    try:
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
                raise PartialInventoryError(requested=amount, allowed=allowed)

        entry = session.get(Inventory, (target_id, item_id))

        if entry:  # If user already have the item
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

        if owns_session:
            session.commit()

        logger.info(
            "ITEM GIVEN: user_id=%s item_id=%s amount=%s overflow=%s",
            target_id, item_id, amount, overflow
        )
    finally:
        if owns_session:
            session.close()

def take_item(target_id: int, item_id: int, amount: int, session=None):
    """
    Removes specified amount of item from target
    """

    if amount < 1:
        raise InvalidItemAmountError

    owns_session = False
    if session is None:
        session = Session()
        owns_session = True

    try:
        if not is_user(target_id, session):
            raise UserNotFoundError(target_id)

        entry = session.get(Inventory, (target_id, item_id))

        if not entry or entry.item_quantity < amount:
            raise NotEnoughItemError

        entry.item_quantity -= amount

        # delete row if it reaches 0
        if entry.item_quantity == 0:
            session.delete(entry)

        if owns_session:
            session.commit()

        logger.info(
            "ITEM TAKEN: user_id=%s item_id=%s amount=%s",
            target_id, item_id, amount
        )
    finally:
        if owns_session:
            session.close()


# Bulk removal of multiple items atomically
def take_items_bulk(target_id: int, items: dict, session):
    """
    Removes multiple items atomically from target.

    items format:
    {
        item_id: amount,
        item_id2: amount2,
        ...
    }

    Requires an external session (will NOT create or commit its own).
    """

    if session is None:
        raise ValueError("take_items_bulk requires an external session")


    # Fetch all relevant inventory rows in one query
    rows = (
        session.query(Inventory)
        .filter(
            Inventory.user_id == target_id,
            Inventory.item_id.in_(items.keys())
        )
        .all()
    )

    inventory_map = {row.item_id: row for row in rows}

    # Validation pass
    for item_id, amount in items.items():
        if amount < 1:
            raise InvalidItemAmountError

        entry = inventory_map.get(item_id)

        if not entry or entry.item_quantity < amount:
            raise NotEnoughItemError

    # Mutation pass (only runs if validation succeeded)
    for item_id, amount in items.items():
        entry = inventory_map[item_id]
        entry.item_quantity -= amount

        if entry.item_quantity == 0:
            session.delete(entry)



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
        if not allow_item_in_inventory(receiver_id, item_id, amount, session):
            return "full_inventory"

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

def fetch_inventory(user_id: int, session=None) -> List[dict]:
    """Returns a list of items in user's inventory (excluding zero quantity).
    If session is provided, it will be reused. Otherwise, a new session is created.
    """

    owns_session = False

    if session is None:
        session = Session()
        owns_session = True

    try:
        inventory = (
            session.query(Inventory, Items)
            .join(Items, Inventory.item_id == Items.item_id)
            .filter(
                Inventory.user_id == user_id,
                Inventory.item_quantity > 0
            )
            .order_by(Items.item_name.asc())
            .all()
        )

        result = []
        for entry, item in inventory:
            result.append({
                "item_id": entry.item_id,
                "item_name": item.item_name,
                "item_quantity": entry.item_quantity,
                "item_rarity": item.item_rarity,
                "item_description": item.item_description,
                "item_icon": item.item_icon
            })

        return result

    finally:
        if owns_session:
            session.close()

def get_inventory(user_id: int, user_name: str) -> Tuple[Optional[str], Optional[discord.Embed]]:
    with Session() as session:
        user = session.get(User, user_id)
        result = fetch_inventory(user_id, session=session)

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
        item_details['amount_owned'] = user_inv.item_quantity if user_inv else 0
    return build_item_info_embed(item_details)

def use_item(user_id: int, item_id: int):
    from utils.usable_items import UsableItemHandler

    with Session() as session:
        try:
            item = session.get(Items, item_id)
            if not item:
                return "That item doesn't exist."

            if not item.item_usable:
                return f"{item.item_name} can’t be used."

            handler = UsableItemHandler.get_handler(item.item_name)
            if not handler:
                return f"{item.item_name} is marked as usable but has no handler (dev issue)."

            # Remove item INSIDE SAME SESSION
            take_item(user_id, item.item_id, 1, session=session)

            # Run item logic
            result = handler(user_id)

            # Commit only after success
            session.commit()

            return result

        except NotEnoughItemError:
            session.rollback()
            return f"You don't have any {item.item_name} left...."

        except Exception:
            session.rollback()
            raise


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

    for _, qty, rarity in rows:
        if qty <= 0:
            continue

        stack_limit = allowed_stack_size(user_pockets.level, rarity)

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