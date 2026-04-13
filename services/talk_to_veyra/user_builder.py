from __future__ import annotations

from sqlalchemy.orm import joinedload

from database.sessionmaker import Session
from domain.friendship.rules import friendship_title_and_progress
from models.users_model import User


def build_chat_user(user_id: int, user_name: str) -> dict:
    """Build conversation-model user payload from Veyra DB state."""
    with Session() as session:
        user = session.get(
            User,
            user_id,
            options=[
                joinedload(User.wallet),
                joinedload(User.friendship),
                joinedload(User.battle_loadout),
            ],
        )

    # Fallback for users that are not yet registered in Veyra DB.
    if user is None:
        return {
            "user_id": user_id,
            "name": user_name,
            "frndship_title": "Stranger",
            "gold": 0,
            "chips": 0,
            "current_energy": 0,
            "exp": 0,
            "lvl": 1,
            "game_events": [],
            "campaign_stage": 1,
            "current_quest": None,
            "loadout": None,
        }

    frndship_exp = user.friendship.friendship_exp if user.friendship else 0
    frndship_title, _ = friendship_title_and_progress(frndship_exp)

    loadout = None
    if user.battle_loadout and (user.battle_loadout.weapon or user.battle_loadout.spell):
        loadout = f"{user.battle_loadout.weapon}/{user.battle_loadout.spell}"

    return {
        "user_id": user.user_id,
        "name": user.user_name,
        "frndship_title": frndship_title,
        "gold": user.wallet.gold if user.wallet else 0,
        "chips": user.wallet.chip if user.wallet else 0,
        "current_energy": user.energy or 0,
        "exp": user.exp or 0,
        "lvl": user.level or 1,
        "game_events": [],
        "campaign_stage": user.campaign_stage or 1,
        "current_quest": None,
        "loadout": loadout,
    }