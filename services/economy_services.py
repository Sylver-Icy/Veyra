from models.users_model import Wallet
from database.sessionmaker import Session
from utils.custom_errors import UserNotFoundError, NegativeGoldError, NotEnoughGoldError, WrongInputError
import logging

logger =  logging.getLogger(__name__)

def add_gold(user_id: int, gold_amount: int):
    "Gives users required amount of gold"
    try:
        gold_amount = int(gold_amount)
    except (TypeError, ValueError):
        raise WrongInputError()

    if gold_amount <= 0:
        raise NegativeGoldError()

    with Session() as session:
        user = session.get(Wallet, user_id)
        if not user:
            logger.warning("User with user id- %s is not registered and was attempted to give %s gold", user_id, gold_amount)
            raise UserNotFoundError(user_id)

        try:
            user.gold += gold_amount
            session.commit()
            return user.gold, gold_amount
        except Exception as e:
            session.rollback()
            logger.error("Error updating %s gold for user- %s: %s", gold_amount, user_id, str(e))

def remove_gold(user_id:int, gold_amount:int):
    try:
        gold_amount = int(gold_amount)
    except (TypeError, ValueError):
        raise WrongInputError()

    if gold_amount <= 0:
        raise NegativeGoldError()

    with Session() as session:
        user = session.get(Wallet,user_id)
        if not user:
            logger.warning("Failed to deduct %s gold from User- %s coz they are not in database", gold_amount, user_id)
            raise UserNotFoundError(user_id)

        if user.gold - gold_amount < 0:
            raise NotEnoughGoldError(gold_amount,user.gold)

        try:
            user.gold -= gold_amount
            session.commit()
            return user.gold, gold_amount
        except Exception as e:
            session.rollback()
            logger.error("Error updating -%s gold for User- %s: %s",gold_amount,user_id,e)

def check_wallet(user_id):
    """Returns how much gold someone has"""
    with Session() as session:
        user = session.get(Wallet,user_id)
        return user.gold

def get_richest_users(limit=10):
    with Session() as session:
        richest_users = (
            session.query(Wallet)
            .order_by(Wallet.gold.desc())
            .limit(limit)
            .all()
        )
        return richest_users

