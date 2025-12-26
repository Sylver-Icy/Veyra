import logging

from database.sessionmaker import Session
from models.users_model import Wallet

from domain.shared.types import Gold
from domain.shared.errors import InvalidAmountError, InsufficientFundsError
from domain.economy.rules import (
    validate_transfer_amount,
    calculate_transfer_fee,
    ensure_can_afford,
)

from utils.custom_errors import (
    UserNotFoundError,
    NegativeGoldError,
    NotEnoughGoldError,
    WrongInputError,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Wallet mutation services
# ---------------------------------------------------------------------------

def add_gold(user_id: int, gold_amount: int):
    """
    Add gold to a user's wallet.

    Args:
        user_id (int): Target user ID
        gold_amount (int): Amount of gold to add

    Returns:
        tuple[Gold, Gold]: (new_balance, added_amount)
    """
    try:
        gold_amount = validate_transfer_amount(gold_amount)
    except InvalidAmountError as exc:
        raise NegativeGoldError from exc

    with Session() as session:
        user = session.get(Wallet, user_id)

        if not user:
            logger.warning(
                "Attempted to add %s gold to non-existent user %s",
                gold_amount,
                user_id,
            )
            raise UserNotFoundError(user_id)

        try:
            user.gold += gold_amount
            session.commit()
            return user.gold, gold_amount
        except Exception as exc:
            session.rollback()
            logger.error(
                "Failed to add %s gold to user %s: %s",
                gold_amount,
                user_id,
                exc,
            )


def remove_gold(user_id: int, gold_amount: int):
    """
    Remove gold from a user's wallet.

    Args:
        user_id (int): Target user ID
        gold_amount (int): Amount of gold to remove

    Returns:
        tuple[Gold, Gold]: (new_balance, removed_amount)
    """
    try:
        gold_amount = validate_transfer_amount(gold_amount)
    except InvalidAmountError as exc:
        raise NegativeGoldError from exc

    with Session() as session:
        user = session.get(Wallet, user_id)

        if not user:
            logger.warning(
                "Attempted to remove %s gold from non-existent user %s",
                gold_amount,
                user_id,
            )
            raise UserNotFoundError(user_id)

        try:
            ensure_can_afford(user.gold, gold_amount)
        except InsufficientFundsError as exc:
            raise NotEnoughGoldError(gold_amount, user.gold) from exc

        try:
            user.gold -= gold_amount
            session.commit()
            return user.gold, gold_amount
        except Exception as exc:
            session.rollback()
            logger.error(
                "Failed to remove %s gold from user %s: %s",
                gold_amount,
                user_id,
                exc,
            )


# ---------------------------------------------------------------------------
# Wallet queries
# ---------------------------------------------------------------------------

def check_wallet(user_id: int) -> Gold:
    """
    Get the current gold balance of a user.

    Args:
        user_id (int): User ID

    Returns:
        Gold: Current balance
    """
    with Session() as session:
        user = session.get(Wallet, user_id)
        return user.gold


def get_richest_users(limit: int = 10):
    """
    Fetch the richest users by gold balance.

    Args:
        limit (int): Maximum number of users to return

    Returns:
        list[Wallet]: Wallets ordered by gold descending
    """
    with Session() as session:
        return (
            session.query(Wallet)
            .order_by(Wallet.gold.desc())
            .limit(limit)
            .all()
        )
