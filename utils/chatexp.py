from datetime import datetime, timezone
import random

from services.exp_services import add_exp
from services.response_services import create_response
on_cooldown = {}  # A dictionary to store users on cooldown

async def chatexp(ctx):
    """
    Grants exp for chatting in servers
    """
    user_id = ctx.author.id
    now = datetime.now(timezone.utc)
    if user_id in on_cooldown:
        last_time = on_cooldown[user_id]
        if (now - last_time).total_seconds() < 30:  # Checks if user is still in cooldown
            return

    await add_exp_with_announcement(ctx, user_id, random.randint(6,15))

    on_cooldown[user_id] = now  # Starts the cooldown till next exp gainp

async def add_exp_with_announcement(ctx, user_id, amount):
    leveled_up = await add_exp(user_id, amount)

    if leveled_up:
        await ctx.send(
            create_response(
                "level_up",
                1,
                user=ctx.author.mention,
                level=leveled_up
            )
        )

    return leveled_up