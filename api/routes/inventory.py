"""
Inventory API Routes

This file exposes HTTP endpoints related to the Veyra economy.
Routes are thin. They validate input, call services, and return schemas.

"""

from fastapi import APIRouter
from api.schemas import (
    InventoryItemSchema,
    InventoryResponse,
)
from services.inventory_services import fetch_inventory


router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
)


@router.get(
    "/{user_id}",
    response_model=InventoryResponse,
)
def get_inventory(user_id: int):
    """
    Get the current inventory of a user.
    """
    inventory = fetch_inventory(user_id)
    items = [
        InventoryItemSchema(
            item_id=i["item_id"],
            name=i["item_name"],
            rarity=i["item_rarity"],
            quantity=i["item_quantity"],
            description=i["item_description"],
        )
        for i in inventory
    ]
    return InventoryResponse(
        user_id=user_id,
        items=items,
  )