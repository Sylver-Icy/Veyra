from models.users_model import User
from database.sessionmaker import Session
import logging

exp_list = [
    0,100, 250, 400, 600, 900, 1250, 1600, 2200, 3000, 4200,
    5500, 7000, 9000, 12000, 15000, 18000, 22000, 27000,
    32000, 38000, 48000, 60000, 78000, 100000
]

logger = logging.getLogger(__name__)

def add_exp(user_id: int, exp_amount: int):
    "Adds exp and handles level up logic"
    with Session() as session:
        user = session.get(User, user_id)
        if not user:
            logger.warning("User ID %s not found", user_id)
            return

        user.exp += exp_amount
        logger.info("%s got %s exp points.", user.user_name, exp_amount)
        current_level = user.level
        new_level = calculate_level(user.exp)

        try:
            if new_level > current_level:
                user.level = new_level
                logger.info("%s has reached level %s", user.user_name, new_level)

            session.commit()
            return new_level if new_level > current_level else None

        except Exception as e:
            session.rollback()
            logger.error("Error updating exp for user %s: %s", user_id, str(e))

def calculate_level(exp: int) -> int:
    current_level = 0
    for threshold in exp_list:
        if exp >= threshold:
            current_level += 1
        else:
            break
    return current_level

def current_exp(user_id: int):
    "Returns current user level and experience point"
    with Session() as session:
        user = session.get(User, user_id)
        return user.exp, user.level
