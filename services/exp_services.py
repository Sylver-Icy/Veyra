from models.users_model import User
from database.sessionmaker import Session
import logging

from domain.progression.rules import calculate_level

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


def current_exp(user_id: int):
    "Returns current user level and experience point"
    with Session() as session:
        user = session.get(User, user_id)
        return user.exp, user.level
