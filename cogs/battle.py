import discord
from discord.ext import commands

from utils.embeds.battleembed import send_battle_challenge

from services.battle.battle_simulation import start_battle_simulation
from services.economy_services import check_wallet, remove_gold, add_gold
from services.users_services import is_user
from services.battle.loadout_services import update_loadout

class Battle(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    @commands.slash_command(description="Challenge someone to a 1v1 battle.")
    async def battle(self, ctx, target: discord.User, bet: int):
        if target.id == ctx.author.id:
            await ctx.respond("Loner ultra pro max plus.", ephemeral = True)
            return
        if target.id == self.bot.user.id:
            await ctx.respond("You ain't gonna win so lets save ourselves some hassle.")
            return
        if not is_user:
            await ctx.respond(f"I can't initiate a battle with {target.display_name} they're not frnds with me.")
            return
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


    @commands.slash_command()
    async def loadout(self, ctx, weapon: str, spell: str):
        result = update_loadout(ctx.author.id, weapon, spell)
        await ctx.respond(result)


def setup(bot):
    bot.add_cog(Battle(bot))