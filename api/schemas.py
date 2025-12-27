"""
API Schemas (DTOs)

This file defines ALL request and response shapes for the Veyra API.

"""
from typing import List, Optional

from pydantic import BaseModel, Field


# -------------------------
# Inventory Schemas
# -------------------------

class InventoryItemSchema(BaseModel):
    item_id: int
    name: str
    rarity: str
    quantity: int
    description: Optional[str] = None


class InventoryResponse(BaseModel):
    user_id: int
    items: List[InventoryItemSchema]


# -------------------------
# Profile Schemas
# -------------------------

class ProfileResponse(BaseModel):
    user_id: int
    username: str
    level: int
    gold: int
    energy: int


class EnergyResponse(BaseModel):
    user_id: int
    current: int
    maximum: int


class FriendshipResponse(BaseModel):
    user_id: int
    title: str
    progress: float


# -------------------------
# Economy Schemas
# -------------------------

class BalanceResponse(BaseModel):
    user_id: int
    gold: int


class TransferGoldRequest(BaseModel):
    from_user_id: int
    to_user_id: int
    amount: int = Field(gt=0, description="Amount of gold to transfer")


class TransferGoldResponse(BaseModel):
    success: bool
    from_user_id: int
    to_user_id: int
    amount: int