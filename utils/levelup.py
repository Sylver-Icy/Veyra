import asyncio

async def give_exp(ctx, user_id: int, exp_amount: int):
    """Adds exp while also checking if level up happened"""
    from services.exp_services import add_exp
    leveled_up = await asyncio.to_thread(add_exp, user_id, exp_amount)

    if leveled_up:
        await ctx.send(f"Congratulations {ctx.author.mention} Levelled up to {leveled_up} yippe 🎉")
