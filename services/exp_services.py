import logging

from database.sessionmaker import Session

from models.users_model import User

from services.jobs_services import JobsClass
from services.refferal_services import get_inviter, mark_inv_successful

from domain.progression.rules import calculate_level

logger = logging.getLogger(__name__)

def handle_level_up(user, new_level: int):
    "Handles all non-Discord side effects of leveling up"
    user.level = new_level
    user = JobsClass(user.user_id)
    user.gain_energy(15)
    if new_level == 5:
        inviter_id = get_inviter(user.user_id)
        mark_inv_successful(inviter_id, user.user_id)
        
    logger.info("%s has reached level %s", user.user_id, new_level)


async def add_exp(user_id: int, exp_amount: int):
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
                handle_level_up(user, new_level)

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
