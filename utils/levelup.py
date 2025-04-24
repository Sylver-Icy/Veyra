async def give_exp(ctx, user_id: str, exp_amount: int):
    from services.exp_services import add_exp
    leveled_up=add_exp(user_id, exp_amount)

    if leveled_up:
        await ctx.send(f"Congratulations {ctx.author.mention} Levelled up to {leveled_up} yippe 🎉")
