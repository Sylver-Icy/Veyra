import logging
from datetime import datetime, timedelta

from models.users_model import UserQuest
from domain.quests.rules import get_random_quest, get_quest_by_id
from database.sessionmaker import Session
from services.economy_services import add_gold
from services.inventory_services import give_item

logger = logging.getLogger(__name__)


def create_quest(session, user_id: int, hardcreate: bool = False):
    """
    Creates a new quest for a user.

    If hardcreate=True, it will delete any active quest and replace it.
    If hardcreate=False, it will only create a quest if no active quest exists.
    """

    # Check for active quest (not completed AND not expired)
    now = datetime.utcnow()

    active_quest = (
        session.query(UserQuest)
        .filter(
            UserQuest.user_id == user_id,
            UserQuest.completed == False,
            UserQuest.expires_at > now
        )
        .first()
    )

    if active_quest:
        if not hardcreate:
            return active_quest
        # Overwrite existing quest
        session.delete(active_quest)
        session.flush()

    # Get a random quest config
    quest_config = get_random_quest()

    duration = quest_config.get("duration_hours", 24)
    expires_at = datetime.utcnow() + timedelta(hours=duration)

    new_quest = UserQuest(
        user_id=user_id,
        quest_id=quest_config["id"],
        progress=0,
        target=quest_config["target"],
        expires_at=expires_at
    )

    session.add(new_quest)
    session.flush()  # let caller control commit lifecycle

    return new_quest



def get_or_create_quest(session, user_id: int):
    """
    Returns the latest quest for a user (expired or not).
    If no quest exists at all, creates one and returns it.
    """

    quest = (
        session.query(UserQuest)
        .filter(UserQuest.user_id == user_id)
        .order_by(UserQuest.started_at.desc())
        .first()
    )

    if quest:
        return quest

    # No quest found at all → create one
    return create_quest(session, user_id, hardcreate=False)


def grant_quest_rewards(user_id: int, quest_id: str, session):
    """
    Distribute all rewards for a completed quest.

    Reads the reward list from quest config and grants each:
      - "gold"  → add_gold()
      - "xp"    → add_exp()
      - "item"  → give_item()

    Args:
        user_id: The user to reward
        quest_id: The quest config ID to look up rewards

    Returns:
        list of reward dicts that were granted, for display purposes
    """
    quest_config = get_quest_by_id(quest_id)
    if not quest_config:
        return []

    rewards = quest_config.get("reward", [])
    granted = []

    for r in rewards:
        reward_type = r.get("type")
        amount = r.get("amount", 0)

        if reward_type == "gold" and amount > 0:
            add_gold(user_id, amount, session)
            granted.append(r)

        elif reward_type == "xp" and amount > 0:
            # lazy import to avoid circular import with exp_services
            from services.exp_services import give_exp
            give_exp(session, user_id, amount)
            granted.append(r)

        elif reward_type == "item":
            item_id = r.get("item_id")
            if item_id and amount > 0:
                try:
                    give_item(user_id, item_id, amount, True, session)
                    granted.append(r)
                except Exception:
                    logger.warning("Failed to give quest reward item %s to user %s", item_id, user_id)

    return granted


def claim_quest_rewards(session, user_id: int):
    """
    Claims rewards for a completed quest that hasn't been claimed yet.
    Returns (granted_rewards_list, quest) on success, (None, None) if nothing to claim.
    """
    quest = (
        session.query(UserQuest)
        .filter(
            UserQuest.user_id == user_id,
            UserQuest.completed == True,
            UserQuest.rewards_claimed == False
        )
        .order_by(UserQuest.completed_at.desc())
        .first()
    )
    if not quest:
        return None, None

    granted = grant_quest_rewards(user_id, quest.quest_id, session)
    quest.rewards_claimed = True
    session.flush()
    return granted, quest


def skip_quest(session, user_id: int):
    """
    Deletes the user's active quest.
    Returns True if a quest was skipped, False if no active quest.
    """
    now = datetime.utcnow()
    quest = (
        session.query(UserQuest)
        .filter(
            UserQuest.user_id == user_id,
            UserQuest.completed == False,
            UserQuest.expires_at > now
        )
        .first()
    )
    if not quest:
        return False

    session.delete(quest)
    session.flush()
    return True


def update_quest_progress(user_id: int, quest_type: str, amount: int = 1, session=None):
    """
    Increment quest progress if the user's active quest matches the given type.

    Args:
        user_id: The user whose quest to update
        quest_type: The action type (e.g. "BATTLE_WIN", "GOLD_EARN", "ITEM_SELL", "LOOTBOX_OPEN")
        amount: How much to increment progress by (default 1)
        session: Optional SQLAlchemy session. If not provided, a new one is created.

    Returns:
        dict with {"completed": bool, "quest": UserQuest} if quest was updated, None otherwise
    """
    owns_session = session is None
    if owns_session:
        session = Session()

    try:
        now = datetime.utcnow()
        quest = (
            session.query(UserQuest)
            .filter(
                UserQuest.user_id == user_id,
                UserQuest.completed == False,
                UserQuest.expires_at > now
            )
            .first()
        )

        if not quest:
            return None

        quest_config = get_quest_by_id(quest.quest_id)
        if not quest_config or quest_config["type"] != quest_type:
            return None

        quest.progress = min(quest.progress + amount, quest.target)

        completed = quest.progress >= quest.target
        if completed:
            quest.completed = True
            quest.completed_at = now

        if owns_session:
            session.commit()

        return {"completed": completed, "quest": quest}

    except Exception:
        if owns_session:
            session.rollback()
        raise

    finally:
        if owns_session:
            session.close()


def decrease_quest_progress(user_id: int, quest_type: str, amount: int = None, session=None):
    """
    Decrease or reset quest progress if the user's active quest matches the given type.

    Args:
        user_id: The user whose quest to update
        quest_type: The action type to match against
        amount: If provided, reduce progress by this amount (clamped at 0).
                If None, reset progress to 0.
        session: Optional SQLAlchemy session.

    Returns:
        UserQuest if updated, None otherwise
    """
    owns_session = session is None
    if owns_session:
        session = Session()

    try:
        now = datetime.utcnow()
        quest = (
            session.query(UserQuest)
            .filter(
                UserQuest.user_id == user_id,
                UserQuest.completed == False,
                UserQuest.expires_at > now
            )
            .first()
        )

        if not quest:
            return None

        quest_config = get_quest_by_id(quest.quest_id)
        if not quest_config or quest_config["type"] != quest_type:
            return None

        if amount is not None:
            quest.progress = max(quest.progress - amount, 0)
        else:
            quest.progress = 0

        if owns_session:
            session.commit()

        return quest

    except Exception:
        if owns_session:
            session.rollback()
        raise

    finally:
        if owns_session:
            session.close()