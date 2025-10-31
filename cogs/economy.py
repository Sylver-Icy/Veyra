import logging
from discord.ext import commands
import discord
from services.economy_services import add_gold, remove_gold, check_wallet
from services.response_services import create_response
from services.users_services import is_user
from utils.custom_errors import VeyraError
from utils.emotes import GOLD_EMOJI

logger = logging.getLogger(__name__)
class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    # @commands.cooldown(1,15,commands.BucketType.user)
    async def checkwallet(self, ctx):
        """Check the wallet balance of the command user."""
        gold = check_wallet(ctx.author.id)
        response = create_response("check_wallet", 1, user=ctx.author.mention, gold=gold, emoji=GOLD_EMOJI)
        await ctx.send(response)



    @commands.slash_command()
    async def transfer_gold(self, ctx, target_user: discord.Member, amount: int):
        """Transfer gold from your wallet to another user. There is a 5% fee"""
        if not is_user(target_user.id):
            await ctx.respond(f"They are not my friend. They don't even have a wallet where am I supposed to send this money to? Hmm <@{ctx.author.id}> ??")
            return
        if amount <=0:
            await ctx.respond("Atleast send 1 gold comeon", ephemeral = True)
            return
        
        if target_user.id == ctx.author.id:
            response = create_response("transfer_gold", 1)
            await ctx.respond(response)
            return

        if target_user.id == self.bot.user.id:
            response = create_response("transfer_gold", 2, user=ctx.author.display_name)
            await ctx.respond(response)
            remove_gold(ctx.author.id, amount)
            logger.info("Gold was given to Veyra", extra={"user": ctx.author.name, "flex": f"Gold amount: {amount}", "cmd": "transfer_gold"})
            return

        try:
            taxed_amount = (5/100)*amount #calculating 5% of total amount
            new_amount = amount-taxed_amount
            user_balance, transferred_gold = remove_gold(ctx.author.id, new_amount)
            target_balance, transferred_gold = add_gold(target_user.id, new_amount)

            response = create_response(
                "transfer_gold",
                3,
                user1=ctx.author.display_name,
                user2=target_user.display_name,
                amount=transferred_gold,
                user1_gold=user_balance,
                user2_gold=target_balance,
                coin_emoji=GOLD_EMOJI,
            )

            await ctx.respond(response)
            logger.info(
            "Gold transferred between two players: Receiver %s",
            target_user.display_name,
            extra={
                "user": ctx.author.name,
                "flex": f"Gold amount: {amount}",
                "cmd": "transfer_gold"
            }
        )
        except VeyraError as e:
            await ctx.respond(str(e))  # TODO: Use procedural error response


def setup(bot):
    bot.add_cog(Economy(bot))