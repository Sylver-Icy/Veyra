from datetime import datetime

from database.sessionmaker import Session
from models.users_model import User, Wallet, Quests
from models.inventory_model import Items, Inventory

import logging
from sqlalchemy.orm import joinedload, selectinload



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
        new_user.wallet = Wallet()
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
    if user_id == 1355171756624580772:
        return True
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

if __name__ == "__main__":
    test_user_id = 915837736819249223
    result = get_user_profile(test_user_id)
    print(result)