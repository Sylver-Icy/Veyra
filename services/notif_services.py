from models.users_model import User

from database.sessionmaker import Session

from utils.embeds.notif.notificationembed import build_notification_embed

import json
from pathlib import Path
from discord.ext.commands import Bot

_NOTIF_CACHE = None


def notif_enabled(user_id: int, session):
    user = session.get(User, user_id)
    return user.notif

def disable_notif(user_id: int):
    with Session() as session:
        user = session.get(User, user_id)
        user.notif = False
        session.commit()

async def send_notification(bot: Bot, user_id: int, notif_key: str, session):
    global _NOTIF_CACHE

    if _NOTIF_CACHE is None:
        notif_path = Path(__file__).parent.parent / "utils/embeds/notif/notifcation.json"
        with open(notif_path, "r", encoding="utf-8") as f:
            _NOTIF_CACHE = json.load(f)

    notif_data = _NOTIF_CACHE

    if notif_key not in notif_data:
        return

    data = notif_data[notif_key]

    embed, view = build_notification_embed(data)

    user = await bot.fetch_user(user_id)
    if not user:
        return

    if not notif_enabled(user_id, session):
        return

    try:
        await user.send(embed=embed, view=view)
    except Exception:
        # User has DMs closed or blocked the bot
        return
