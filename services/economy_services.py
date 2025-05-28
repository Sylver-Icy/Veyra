from models.users_model import Wallet
from database.sessionmaker import Session
from utils.custom_errors import UserNotFoundError, NegativeGoldError, NotEnoughGoldError
import logging

logger =  logging.getLogger(__name__)

def add_gold(user_id: int, gold_amount: int):
    "Gives users required amount of gold"
    if not isinstance(gold_amount, int) or gold_amount <= 0:
        logger.warning("Invalid gold amount: %s", gold_amount)
        raise NegativeGoldError("Gold amount must be a positive integer.")
    
    with Session() as session:
        user = session.get(Wallet, user_id)
        if not user:
            logger.warning("User with user id- %s is not registered and was attempted to give %s gold", user_id, gold_amount)
            raise UserNotFoundError("User is not registered")

        try:
            user.gold += gold_amount
            session.commit()
            return user.gold, gold_amount
        except Exception as e:
            session.rollback()
            logger.error("Error updating %s gold for user- %s: %s", gold_amount, user_id, str(e))

def remove_gold(user_id:int, gold_amount:int):
    if not isinstance(gold_amount, int) or gold_amount <=0:
        raise NegativeGoldError(f"Failed to deduct {gold_amount} gold from user- {user_id}")
    
    with Session() as session:
        user = session.get(Wallet,user_id)
        if not user:
            logger.warning("Failed to deduct %s gold from User- %s coz they are not in database", gold_amount, user_id)
            raise UserNotFoundError(f"User-{user_id} is not registered can't deduct gold")
        
        if user.gold - gold_amount < 0:
            raise NotEnoughGoldError(gold_amount,user.gold)
        
        try:
            user.gold -= gold_amount
            session.commit()
            return user.gold, gold_amount
        except Exception as e:
            session.rollback()
            logger.error("Error updating -%s gold for User- %s: %s",gold_amount,user_id,e)
