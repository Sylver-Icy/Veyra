from discord.ext import commands
import discord
import logging
from services.economy_services import add_gold, remove_gold, check_wallet
from utils.custom_errors import VeyraError
from utils.emotes import GOLD_EMOJI
from services.response_serives import create_response

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def checkwallet(self, ctx):
        gold = check_wallet(ctx.author.id)
        response = create_response("check_wallet", 1, user=ctx.author.mention, gold=gold, emoji=GOLD_EMOJI)
        await ctx.send(response)

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
           response = create_response("transfer_gold",1) #create response for when someone tries to send money to themselve
           await ctx.respond(response)
           return
        if target_user.id == self.bot.user.id:
            response = create_response("transfer_gold",2,user=ctx.author.display_name) #create response for when someone sends money to veyra
            await ctx.respond(response)
            remove_gold(ctx.author.id, amount)
            return
        try:
            user_balance, transferred_gold = remove_gold(ctx.author.id, amount)
            target_balance, transferred_gold = add_gold(target_user.id, amount)
            response = create_response(  #create response for when users do transactions with other users
                "transfer_gold",
                3,
                user1=ctx.author.display_name,
                user2=target_user.display_name,
                amount=transferred_gold,
                user1_gold = user_balance,
                user2_gold = target_balance,
                coin_emoji = GOLD_EMOJI
                )
            
            await ctx.respond(response)
        except VeyraError as e:
            await ctx.respond(str(e))

def setup(bot):
    bot.add_cog(Economy(bot))