from discord.ext import commands
import discord
import logging
from services.economy_services import add_gold, remove_gold, check_wallet
from utils.custom_errors import VeyraError

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def checkwallet(self, ctx):
        gold = check_wallet(ctx.author.id)
        await ctx.send(f"You currently have {gold} gold")

    @commands.slash_command()
    async def give_gold(self, ctx, target_user: discord.Member, amount: int):
        """Freee Gold!!!!!"""
        if target_user.id == self.bot.user.id:
           await ctx.respond("I don't need it fk offf")
           return
        try:
            new_gold, transferred_gold = add_gold(target_user.id, amount)
            await ctx.respond(f"✅ Gave {transferred_gold} gold to {target_user.display_name}. New balance: {new_gold}")
        except VeyraError as e:
            await ctx.respond(str(e))

    @commands.slash_command()
    async def transfer_gold(self, ctx, target_user: discord.Member, amount: int):
        """Transfers gold to target user from command user's wallet"""
        if target_user.id == ctx.author.id:
           await ctx.respond("How exactly are you planning to give your money to yourself???")
           return
        if target_user.id == self.bot.user.id:
            await ctx.respond("Awwww Sweetie tysm:3")
            remove_gold(ctx.author.id, amount)
            return
        try:
            user_balance, transferred_gold = remove_gold(ctx.author.id, amount)
            target_balance, transferred_gold = add_gold(target_user.id, amount)
            await ctx.respond(
                f"{ctx.author} transferred {transferred_gold} gold to {target_user.display_name}.\n"
                f"Updated Balance — {ctx.author.display_name}: {user_balance}, {target_user.display_name}: {target_balance}"
            )
        except VeyraError as e:
            await ctx.respond(str(e))

def setup(bot):
    bot.add_cog(Economy(bot))