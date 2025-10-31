import discord
from discord.ext import commands
from utils.embeds.battleembed import send_battle_challenge
from services.battle.battle_simulation import start_battle_simulation
from services.economy_services import check_wallet, remove_gold, add_gold

class Battle(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    @commands.slash_command(description="Challenge someone to a 1v1 battle.")
    async def battle(self, ctx, target: discord.User, bet: int):
        if bet <= 0:
            await ctx.respond("Bruh don't gamble if you can't afford T-T", ephemeral=True)
            return

        if bet > check_wallet(ctx.author.id):
            await ctx.respond ("You don't have enough gold to initiate the challege. Try betting lower.", ephemeral=True)
            return

        remove_gold(ctx.author.id, bet) #take gold for pot money
        result = await send_battle_challenge(ctx, ctx.author.id, target.id, bet)
        if result is True:
            await ctx.send(f"🔥 {ctx.author.mention} vs {target.mention} — the battle begins!")
            await start_battle_simulation(ctx, ctx.author, target, bet)
        elif result is False:
            add_gold(ctx.author.id, bet)
            await ctx.send(f"{ctx.author.mention}, your challenge was rejected. You pot money was refunded.")
        else:
            await ctx.send("No response. Challenge expired. Refunding pot gimme a moment.")
            add_gold(ctx.author.id, bet)



def setup(bot):
    bot.add_cog(Battle(bot))