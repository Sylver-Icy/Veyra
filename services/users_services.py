from datetime import datetime

from database.sessionmaker import Session
from models.users_model import User
import logging

logger = logging.getLogger(__name__)

def add_user(user_id: int, user_name: str):
    """
    Func to add a user to database.
    It adds new user directly to database.
    """
    with Session() as session:
        new_user = User(
            user_id=user_id,
            user_name=user_name,
            joined=datetime.utcnow()
        )
        session.add(new_user)
        try:
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error("Error adding user %s: %s", user_id, str(e))

def is_user(user_id: int):
    """
    Func to check if a user exists in the database.
    It queries the database directly.
    """
    with Session() as session:
        return session.get(User, user_id) is not None
