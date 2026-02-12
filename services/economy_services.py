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

def add_gold(user_id: int, gold_amount: int, session=None):
    """Add gold to a user's wallet.

    Args:
        user_id (int): Target user ID
        gold_amount (int): Amount of gold to add
        session: Optional SQLAlchemy session to use. If not provided, a new session is created.

    Returns:
        tuple[Gold, Gold]: (new_balance, added_amount)
    """
    try:
        gold_amount = validate_transfer_amount(gold_amount)
    except InvalidAmountError as exc:
        raise NegativeGoldError from exc

    owns_session = session is None

    # If a session is provided, use it (do not commit/rollback here because the caller owns it).
    if owns_session:
        session = Session()

    try:
        stmt = (
            update(Wallet)
            .where(Wallet.user_id == user_id)
            .values(gold=Wallet.gold + gold_amount)
            .returning(Wallet.gold)
        )
        result = session.execute(stmt).first()
        if result is None:
            logger.warning(
                "Attempted to add %s gold to non-existent user %s",
                gold_amount,
                user_id,
            )
            raise UserNotFoundError(user_id)
        new_balance = result[0]
        if owns_session:
            session.commit()
        return new_balance, gold_amount

    except Exception:
        if owns_session:
            session.rollback()
        raise

    finally:
        if owns_session:
            session.close()


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

    owns_session = session is None

    if owns_session:
        session = Session()

    try:
        stmt = (
            update(Wallet)
            .where(Wallet.user_id == user_id)
            .where(Wallet.gold >= gold_amount)
            .values(gold=Wallet.gold - gold_amount)
            .returning(Wallet.gold)
        )
        result = session.execute(stmt).first()
        if result is None:
            user_exists = session.get(Wallet, user_id) is not None
            if not user_exists:
                raise UserNotFoundError(user_id)
            raise NotEnoughGoldError(gold_amount, "gold")
        new_balance = result[0]
        if owns_session:
            session.commit()
        return new_balance, gold_amount

    except Exception:
        if owns_session:
            session.rollback()
        raise

    finally:
        if owns_session:
            session.close()


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
        sender = (
            session.query(Wallet)
            .filter(Wallet.user_id == sender_id)
            .with_for_update()
            .one_or_none()
        )
        receiver = (
            session.query(Wallet)
            .filter(Wallet.user_id == receiver_id)
            .with_for_update()
            .one_or_none()
        )

        if not sender:
            raise UserNotFoundError(sender_id)
        if not receiver:
            raise UserNotFoundError(receiver_id)

        net_amount, fee = calculate_transfer_fee(amount)

        sender_stmt = (
            update(Wallet)
            .where(Wallet.user_id == sender_id)
            .where(Wallet.gold >= amount)
            .values(gold=Wallet.gold - amount)
        )
        sender_result = session.execute(sender_stmt)
        if sender_result.rowcount == 0:
            raise NotEnoughGoldError(amount, sender.gold)

        receiver_stmt = (
            update(Wallet)
            .where(Wallet.user_id == receiver_id)
            .values(gold=Wallet.gold + net_amount)
        )
        session.execute(receiver_stmt)

        try:
            session.commit()

            sender_balance = session.get(Wallet, sender_id).gold
            receiver_balance = session.get(Wallet, receiver_id).gold

            return TransferResult(
                sender_balance=sender_balance,
                receiver_balance=receiver_balance,
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
        if not user:
            raise UserNotFoundError(user_id)
        return user.gold


def check_wallet_full(user_id: int, session = None):
    if session is not None:
        user = session.get(Wallet, user_id)
        return user.gold, user.chip

    with Session() as session:
        user = session.get(Wallet, user_id)
        return user.gold, user.chip

def add_chip(user_id: int, amount: int, session = None):
    owns_session = session is None

    if owns_session:
        session = Session()

    try:
        stmt = (
            update(Wallet)
            .where(Wallet.user_id == user_id)
            .values(chip=Wallet.chip + amount)
        )
        result = session.execute(stmt)
        if result.rowcount == 0:
            raise UserNotFoundError(user_id)
        if owns_session:
            session.commit()
    except Exception:
        if owns_session:
            session.rollback()
        raise
    finally:
        if owns_session:
            session.close()


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
            .where(Wallet.user_id == user_id)
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
