from datetime import datetime, timedelta
from models.users_model import UserQuest
from domain.quests.rules import get_random_quest


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
