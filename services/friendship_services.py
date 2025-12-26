from database.sessionmaker import Session
from models.users_model import Friendship
from services.users_services import is_user

from domain.friendship.rules import (
    can_gain_friendship_today,
    friendship_title_and_progress,
)


# ---------------------------------------------------------------------------
# Friendship mutation services
# ---------------------------------------------------------------------------

def add_friendship(user_id: int, exp: int):
    """
    Add friendship EXP to a user, respecting daily caps.

    Args:
        user_id (int): Target user ID
        exp (int): Friendship EXP to add

    Returns:
        int | None:
            - EXP actually added
            - 0 if daily cap reached
            - None if user is not registered
    """
    if not is_user(user_id):
        return  # No friendship if user is not registered

    with Session() as session:
        user = session.get(Friendship, user_id)

        if user:
            if not can_gain_friendship_today(user.daily_exp):
                return 0  # Daily cap reached

            user.friendship_exp += exp
            user.daily_exp += exp
            session.commit()
            return exp

        # New user entry
        new_entry = Friendship(
            user_id=user_id,
            friendship_exp=exp,
            daily_exp=exp,
        )
        session.add(new_entry)
        session.commit()
        return exp


# ---------------------------------------------------------------------------
# Friendship queries
# ---------------------------------------------------------------------------

def check_friendship(user_id: int):
    """
    Fetch the friendship title and progress for a user.

    Args:
        user_id (int): Target user ID

    Returns:
        tuple[str, float]: (title, progress)
    """
    with Session() as session:
        user = session.get(Friendship, user_id)

        if user:
            exp = user.friendship_exp
            title, progress = friendship_title_and_progress(exp)
            return title, progress

        return "Stranger", 0.0


def reset_all_daily_exp():
    """
    Reset daily friendship EXP for all users.
    Intended for daily reset jobs.
    """
    with Session() as session:
        session.query(Friendship).update({Friendship.daily_exp: 0})
        session.commit()