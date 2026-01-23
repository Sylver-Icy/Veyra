import logging
from discord.ext import commands
import discord
from discord import ui
from services.economy_services import add_gold, remove_gold
from services.response_services import create_response
from services.users_services import is_user
from services.friendship_services import add_friendship


from utils.custom_errors import VeyraError
from utils.emotes import GOLD_EMOJI
from utils.embeds.leaderboard.leaderboardembed import gold_leaderboard_embed
from utils.embeds.loanembed import build_loan_terms_embed

from domain.guild.commands_policies import non_spam_command

logger = logging.getLogger(__name__)
class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.slash_command()
    @commands.cooldown(1,120,commands.BucketType.user)
    @non_spam_command()
    async def leaderboard(self,ctx):
        embed = await gold_leaderboard_embed(self.bot)
        await ctx.respond(embed=embed)


    class StarterLoanTermsView(ui.View):
        def __init__(self, cog: "Economy"):
            super().__init__(timeout=60)
            self.cog = cog

        @ui.button(label="Accept Terms", style=discord.ButtonStyle.green)
        async def accept_terms(self, button: ui.Button, interaction: discord.Interaction):
            # Open the confirmation modal
            await interaction.response.send_modal(Economy.StarterLoanModal(self.cog))


    class StarterLoanModal(ui.Modal):
        def __init__(self, cog: "Economy"):
            super().__init__(title="Loan Confirmation")
            self.cog = cog

            self.confirm = ui.InputText(
                label="Type CONFIRM to accept",
                placeholder="CONFIRM",
                required=True,
                max_length=16,
            )
            self.add_item(self.confirm)

        async def callback(self, interaction: discord.Interaction):
            value = (self.confirm.value or "").strip().upper()
            if value != "CONFIRM":
                await interaction.response.send_message(
                    "Loan cancelled. Type **CONFIRM** exactly if you want the starter loan.",
                    ephemeral=True,
                )
                return

            # Grant starter loan
            principal = 2000
            term_days = 7

            # NOTE: This only grants gold. Persisting loans/credit score should be handled
            # by your upcoming loan service + DB schema.
            new_balance, _ = add_gold(interaction.user.id, principal)

            await interaction.response.send_message(
                f"✅ **Starter Pack Loan Granted!**\n\n"
                f"You received **{principal}{GOLD_EMOJI}**.\n"
                f"Repay within **{term_days} days** (no interest).\n"
                f"Failing to repay will **hurt your credit score** and you'll be **locked out of loans**.\n\n"
                f"Your new balance: **{new_balance}{GOLD_EMOJI}**",
                ephemeral=True,
            )


    @commands.slash_command(name="loan")
    @non_spam_command()
    async def loan(self, ctx: discord.ApplicationContext):
        """Take a starter pack loan (one-time). Shows terms before confirmation."""

        embed = build_loan_terms_embed()

        view = self.StarterLoanTermsView(self)
        await ctx.respond(embed=embed, view=view)


    @commands.slash_command()
    @non_spam_command()
    async def transfer_gold(self, ctx, target_user: discord.Member, amount: int):
        """Transfer gold from your wallet to another user. There is a 5% fee"""
        if target_user.id == self.bot.user.id:
            response = create_response("transfer_gold", 2, user=ctx.author.display_name)
            await ctx.respond(response)
            remove_gold(ctx.author.id, amount)
            logger.info("Gold was given to Veyra", extra={"user": ctx.author.name, "flex": f"Gold amount: {amount}", "cmd": "transfer_gold"})

            if amount >= 10:
                friendship_gain = amount // 10  # 1 EXP per 10 gold
                add_friendship(ctx.author.id, friendship_gain)

            add_friendship(ctx.author.id, 1)

            return

        if not is_user(target_user.id):
            await ctx.respond(f"They are not my friend. They don't even have a wallet where am I supposed to send this money to? Hmm <@{ctx.author.id}> ??")
            return
        if amount <=0:
            await ctx.respond("Atleast send 1 gold come on", ephemeral = True)
            return

        if target_user.id == ctx.author.id:
            response = create_response("transfer_gold", 1)
            await ctx.respond(response)
            return


        try:
            new_amount = int(amount * 0.95)  #calculating 5% of total amount
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