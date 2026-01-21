"""User services.

This module contains helper functions for creating users and updating user-related
statistics in the database.
"""

import logging
from datetime import datetime

from sqlalchemy import func, update
from sqlalchemy.orm import joinedload, selectinload

from database.sessionmaker import Session
from models.inventory_model import Inventory
from models.users_model import Quests, User, UserStats, Wallet

from domain.friendship.rules import friendship_title_and_progress

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
        new_user = User(user_id=user_id, user_name=user_name, joined=datetime.utcnow())
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


def is_user(user_id: int, session=None) -> bool:
    """Check if a user exists in the database.

    If a session is provided, it will be used (and NOT closed here).
    Otherwise this function creates its own session.

    Args:
        user_id: Discord user id.
        session: Optional active SQLAlchemy session.

    Returns:
        True if the user exists, False otherwise.
    """

    if session is not None:
        return session.get(User, user_id) is not None

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

        quest = session.query(Quests).filter(Quests.user_id == user_id).one_or_none()

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
            "friendship_exp": user.friendship.friendship_exp if user.friendship else 0,
            "loadout": {
                "weapon": user.battle_loadout.weapon,
                "spell": user.battle_loadout.spell,
                "win_streak": user.battle_loadout.win_streak,
            }
            if user.battle_loadout
            else None,
            "inventory_preview": inventory_preview,
            "quest": {
                "delivery_items": quest.delivery_items,
                "reward": quest.reward,
                "limit": quest.limit,
                "skips": quest.skips,
                "streak": quest.streak,
            }
            if quest
            else None,
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
                longest_quest_streak=func.greatest(UserStats.longest_quest_streak, new_streak),
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
                biggest_lottery_win=func.greatest(UserStats.biggest_lottery_win, new_amount),
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


def get_user_profile_new(user_id: int) -> dict:
    """Fetch an embed-friendly snapshot of a user's profile.

    This is intended as a single data source for building Discord embeds/UI.
    It loads all meaningful progression and statistics in one query where possible.

    Args:
        user_id: Discord user id.

    Returns:
        A dictionary containing user profile + stats.

    Raises:
        ValueError: If the user does not exist.
    """

    with Session() as session:
        user = (
            session.query(User)
            .options(
                joinedload(User.wallet),
                joinedload(User.friendship),
                joinedload(User.battle_loadout),
                joinedload(User.user_stats),
                selectinload(User.inventory).joinedload(Inventory.item),
            )
            .filter(User.user_id == user_id)
            .one_or_none()
        )

        if not user:
            raise ValueError("User not found")



        # Ensure stats row exists for older users and keep payload consistent.
        if getattr(user, "user_stats", None) is None:
            ensure_user_stats(session, user_id)
            user.user_stats = session.get(UserStats, user_id)


        if user.inventory:
            total_items = sum(inv.item_quantity for inv in user.inventory)
            unique_items = len(user.inventory)  #each row = one unique item_id
        else:
            total_items = 0
            unique_items = 0

        friendship_exp = user.friendship.friendship_exp if user.friendship else 0
        friendship_title, progress = friendship_title_and_progress(friendship_exp)

        stats = user.user_stats

        return {
            "identity": {
                "user_id": user.user_id,
                "user_name": user.user_name,
                "joined": user.joined,
            },
            "progression": {
                "level": user.level,
                "exp": user.exp,
                "energy": user.energy,
                "campaign_stage": user.campaign_stage,
                "friendship": {
                    "progress": progress,
                    "title": friendship_title,
                },
            },
            "inventory_summary": {
            "total_items": total_items,
            "unique_items": unique_items
        },
            "economy": {"gold": user.wallet.gold if user.wallet else 0},
            "battle": {
            "loadout": (
                {
                    "weapon": user.battle_loadout.weapon,
                    "spell": user.battle_loadout.spell,
                    "win_streak": user.battle_loadout.win_streak,
                }
                if user.battle_loadout
                else {
                    "weapon": "Training Blade",
                    "spell": "Nightfall",
                    "win_streak": 0,
                }
            )
            },
            "stats": {
                "battles_won": stats.battles_won if stats else 0,
                "races_won": stats.races_won if stats else 0,
                "longest_quest_streak": stats.longest_quest_streak if stats else 0,
                "weekly_rank1_count": stats.weekly_rank1_count if stats else 0,
                "biggest_lottery_win": stats.biggest_lottery_win if stats else 0,
                "updated_at": stats.updated_at if stats else None,
            },
        }


if __name__ == "__main__":
    import json

    TEST_USER_ID = 915837736819249223

    try:
        profile = get_user_profile_new(TEST_USER_ID)
        print(json.dumps(profile, default=str, indent=2))
    except Exception as e:
        logger.exception("Failed to fetch profile for user_id=%s", TEST_USER_ID)
        raise