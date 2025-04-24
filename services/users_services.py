from datetime import datetime

from database.sessionmaker import Session
from models.users_model import User

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
        session.commit()

def is_user(user_id: int):
    """
    Func to check if a user exists in the database.
    It queries the database directly.
    """
    with Session() as session:
        return session.get(User, user_id) is not None

print(is_user(123))