from services.response_services import create_response
import asyncio

async def give_exp(ctx, user_id: int, exp_amount: int):
    """Adds exp while also checking if level up happened"""
    from services.exp_services import add_exp
    leveled_up = await asyncio.to_thread(add_exp, user_id, exp_amount)

    if leveled_up:
        await ctx.send(create_response("level_up",1,user=ctx.author.mention,level=leveled_up))