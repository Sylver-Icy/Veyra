import discord
from discord.ext import commands
from utils.embeds.battleembed import send_battle_challenge
from services.battle.battle_simulation import start_battle_simulation

class Battle(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    @commands.slash_command(description="Challenge someone to a 1v1 battle.")
    async def duel(self, ctx, target: discord.User, bet: int):
        result = await send_battle_challenge(ctx, ctx.author.id, target.id, bet)
        if result is True:
            await ctx.send(f"🔥 {ctx.author.mention} vs {target.mention} — the battle begins!")
            await start_battle_simulation(ctx, ctx.author, target, bet)
        elif result is False:
            await ctx.send(f"{ctx.author.mention}, your challenge was rejected.")
        else:
            await ctx.send("No response. Challenge expired.")


def setup(bot):
    bot.add_cog(Battle(bot))