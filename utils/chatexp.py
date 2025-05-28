from datetime import datetime, timezone
import random

from utils.levelup import give_exp

on_cooldown = {}  # A dictionary to store users on cooldown

async def chatexp(ctx):
    """
    Grants exp for chatting in servers
    """
    user_id = ctx.author.id
    now = datetime.now(timezone.utc)
    if user_id in on_cooldown:
        last_time = on_cooldown[user_id]
        if (now - last_time).total_seconds() < 60:  # Checks if user is still in cooldown
            return

    await give_exp(ctx, user_id, random.randint(6, 15))  # Grants random amount of exp from 6 to 15

    on_cooldown[user_id] = now  # Starts the cooldown till next exp gainp