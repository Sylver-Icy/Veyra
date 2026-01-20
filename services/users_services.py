"""User services.

This module contains helper functions for creating users and updating user-related
statistics in the database.
"""

import logging

from datetime import datetime

from sqlalchemy import update, func
from sqlalchemy.orm import joinedload, selectinload

from database.sessionmaker import Session
from models.users_model import User, Wallet, Quests, UserStats
from models.inventory_model import Inventory


logger = logging.getLogger(__name__)


def ensure_user_stats(session, user_id: int) -> None:
    """Ensure a UserStats row exists for the given user.

    This prevents silent no-op updates when older users exist without a stats row
    (e.g., after introducing the user_stats table).

    Args:
        session: An active SQLAlchemy session.
        user_id: Discord user id.
    """
    existing = session.get(UserStats, user_id)
    if existing is None:
        session.add(UserStats(user_id=user_id))
        session.flush()


def add_user(user_id: int, user_name: str):
    """Create a new user and related rows (wallet, stats).

    Args:
        user_id: Discord user id.
        user_name: Discord username.

    Returns:
        True if created successfully, False otherwise.
    """
    with Session() as session:
        new_user = User(
            user_id=user_id,
            user_name=user_name,
            joined=datetime.utcnow()
        )
        new_user.wallet = Wallet()
        new_user.user_stats = UserStats()
        session.add(new_user)
        try:
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            logger.error("Error adding user %s: %s", user_id, str(e))
            return False


def is_user(user_id: int):
    """
    Func to check if a user exists in the database.
    It queries the database directly.
    """
    with Session() as session:
        return session.get(User, user_id) is not None




def get_user_profile(user_id: int) -> dict:
    with Session() as session:
        user = (
            session.query(User)
            .options(
                joinedload(User.wallet),
                joinedload(User.friendship),
                joinedload(User.battle_loadout),
                selectinload(User.inventory).joinedload(Inventory.item),
            )
            .filter(User.user_id == user_id)
            .one_or_none()
        )

        if not user:
            raise ValueError("User not found")

        quest = (
            session.query(Quests)
            .filter(Quests.user_id == user_id)
            .one_or_none()
        )

        inventory_preview = [
            {
                "name": inv.item.item_name,
                "count": inv.item_quantity,
            }
            for inv in user.inventory[:5]
        ]

        return {
            "user_name": user.user_name,
            "exp": user.exp,
            "level": user.level,
            "gold": user.wallet.gold if user.wallet else 0,
            "friendship_exp": (
                user.friendship.friendship_exp if user.friendship else 0
            ),
            "loadout": {
                "weapon": user.battle_loadout.weapon,
                "spell": user.battle_loadout.spell,
                "win_streak": user.battle_loadout.win_streak,
            } if user.battle_loadout else None,
            "inventory_preview": inventory_preview,
            "quest": {
                "delivery_items": quest.delivery_items,
                "reward": quest.reward,
                "limit": quest.limit,
                "skips": quest.skips,
                "streak": quest.streak,
            } if quest else None,
        }


def update_longest_quest_streak(user_id: int, new_streak: int) -> None:
    """Update the user's longest quest streak if the new streak is higher.

    Args:
        user_id: Discord user id.
        new_streak: The user's current quest streak.
    """
    with Session() as session:
        ensure_user_stats(session, user_id)
        session.execute(
            update(UserStats)
            .where(UserStats.user_id == user_id)
            .values(
                longest_quest_streak=func.greatest(
                    UserStats.longest_quest_streak, new_streak
                ),
                updated_at=func.now(),
            )
        )
        session.commit()


def update_biggest_lottery_win(user_id: int, new_amount: int) -> None:
    """Update the user's biggest lottery win if the new amount is higher.

    Args:
        user_id: Discord user id.
        new_amount: Amount won in the latest lottery.
    """
    with Session() as session:
        ensure_user_stats(session, user_id)
        session.execute(
            update(UserStats)
            .where(UserStats.user_id == user_id)
            .values(
                biggest_lottery_win=func.greatest(
                    UserStats.biggest_lottery_win, new_amount
                ),
                updated_at=func.now(),
            )
        )
        session.commit()


def inc_battles_won(user_id: int, amount: int = 1) -> None:
    """Increment the user's battle wins counter.

    Args:
        user_id: Discord user id.
        amount: Increment amount.
    """
    with Session() as session:
        ensure_user_stats(session, user_id)
        session.execute(
            update(UserStats)
            .where(UserStats.user_id == user_id)
            .values(
                battles_won=UserStats.battles_won + amount,
                updated_at=func.now(),
            )
        )
        session.commit()


def inc_races_won(user_id: int, amount: int = 1) -> None:
    """Increment the user's race wins counter.

    Args:
        user_id: Discord user id.
        amount: Increment amount.
    """
    with Session() as session:
        ensure_user_stats(session, user_id)
        session.execute(
            update(UserStats)
            .where(UserStats.user_id == user_id)
            .values(
                races_won=UserStats.races_won + amount,
                updated_at=func.now(),
            )
        )
        session.commit()


def inc_top_leaderboard(user_id: int, amount: int = 1) -> None:
    """Increment the count of weekly leaderboard #1 placements.

    Args:
        user_id: Discord user id.
        amount: Increment amount.
    """
    with Session() as session:
        ensure_user_stats(session, user_id)
        session.execute(
            update(UserStats)
            .where(UserStats.user_id == user_id)
            .values(
                weekly_rank1_count=UserStats.weekly_rank1_count + amount,
                updated_at=func.now(),
            )
        )
        session.commit()