import logging
from sqlalchemy import update

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
    NotEnoughGoldError,
    NegativeGoldError
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
            raise


def remove_gold(user_id: int, gold_amount: int, session=None):
    """
    Remove gold from a user's wallet.

    Args:
        user_id (int): Target user ID
        gold_amount (int): Amount of gold to remove
        session: Optional SQLAlchemy session to use. If not provided, a new session is created.

    Returns:
        tuple[Gold, Gold]: (new_balance, removed_amount)
    """
    try:
        gold_amount = validate_transfer_amount(gold_amount)
    except InvalidAmountError as exc:
        raise NegativeGoldError from exc

    # If a session is provided, use it (do not commit/rollback here because the caller owns it).
    if session is not None:
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

        user.gold -= gold_amount
        return user.gold, gold_amount

    # Otherwise, create and manage our own session.
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
            raise


# ---------------------------------------------------------------------------
# Gold transfer service
# ---------------------------------------------------------------------------

def transfer_gold(sender_id: int, receiver_id: int, amount: int):
    """
    Transfer gold from one user to another with a transaction fee applied.

    Args:
        sender_id (int): User ID sending gold
        receiver_id (int): User ID receiving gold
        amount (int): Raw amount of gold to transfer (before fee)

    Returns:
        TransferResult: Final balances and transfer details
    """
    from domain.economy.entities import TransferResult

    try:
        amount = validate_transfer_amount(amount)
    except InvalidAmountError as exc:
        raise NegativeGoldError from exc

    with Session() as session:
        sender = session.get(Wallet, sender_id)
        receiver = session.get(Wallet, receiver_id)

        if not sender:
            raise UserNotFoundError(sender_id)
        if not receiver:
            raise UserNotFoundError(receiver_id)

        net_amount, fee = calculate_transfer_fee(amount)

        try:
            ensure_can_afford(sender.gold, amount)
        except InsufficientFundsError as exc:
            raise NotEnoughGoldError(amount, sender.gold) from exc

        try:
            sender.gold -= amount
            receiver.gold += net_amount

            session.commit()

            return TransferResult(
                sender_balance=sender.gold,
                receiver_balance=receiver.gold,
                amount_transferred=net_amount,
                fee_charged=fee,
            )

        except Exception as exc:
            session.rollback()
            logger.error(
                "Failed to transfer %s gold from %s to %s: %s",
                amount,
                sender_id,
                receiver_id,
                exc,
            )
            raise


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


def check_wallet_full(user_id: int, session = None):
    if session is not None:
        user = session.get(Wallet, user_id)
        return user.gold, user.chip

    with Session() as session:
        user = session.get(Wallet, user_id)
        return user.gold, user.chip

def add_chip(user_id: int, amount: int, session = None):
    if session is not None:
        user = session.get(Wallet, user_id)
        user.chip += amount
        return

    with Session() as session:
        user = session.get(Wallet, user_id)
        user.chip += amount
        session.commit()


def remove_chips(user_id: int, amount: int, session=None):
    """
    Truly atomic chip removal.
    Uses a single UPDATE statement guarded by chips >= amount.
    Prevents race-condition double spends.
    """
    try:
        amount = validate_transfer_amount(amount)
    except InvalidAmountError as exc:
        raise NegativeGoldError from exc

    owns_session = session is None
    if owns_session:
        session = Session()

    try:
        stmt = (
            update(Wallet)
            .where(Wallet.id == user_id)
            .where(Wallet.chip >= amount)
            .values(chip=Wallet.chip - amount)
            .returning(Wallet.chip)
        )

        result = session.execute(stmt).first()

        if result is None:
            # Could be user not found OR not enough chips
            # So detect existence:
            user_exists = session.get(Wallet, user_id) is not None
            if not user_exists:
                raise UserNotFoundError(user_id)
            raise NotEnoughGoldError(amount, "chip")

        new_balance = result[0]

        if owns_session:
            session.commit()

        return new_balance, amount

    except Exception:
        if owns_session:
            session.rollback()
        raise
    finally:
        if owns_session:
            session.close()

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
