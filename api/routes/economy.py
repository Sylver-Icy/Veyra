

"""
Economy API Routes

This file exposes HTTP endpoints related to the Veyra economy.
Routes are thin. They validate input, call services, and return schemas.

"""

from fastapi import APIRouter
from api.schemas import (
    BalanceResponse,
    TransferGoldRequest,
    TransferGoldResponse,
)
from services.economy_services import check_wallet, transfer_gold


router = APIRouter(
    prefix="/economy",
    tags=["economy"],
)


@router.get(
    "/balance/{user_id}",
    response_model=BalanceResponse,
)
def get_balance(user_id: int):
    """
    Get the current gold balance of a user.
    """
    gold = check_wallet(user_id)

    return BalanceResponse(
        user_id=user_id,
        gold=gold,
    )


@router.post(
    "/transfer",
    response_model=TransferGoldResponse,
)
def transfer_gold_api(payload: TransferGoldRequest):
    """
    Transfer gold from one user to another.
    """
    transfer_gold(
        sender_id=payload.from_user_id,
        receiver_id=payload.to_user_id,
        amount=payload.amount,
    )

    return TransferGoldResponse(
        success=True,
        from_user_id=payload.from_user_id,
        to_user_id=payload.to_user_id,
        amount=payload.amount,
    )