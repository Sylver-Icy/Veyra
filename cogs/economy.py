"""economy.py

Economy-related commands (leaderboard, starter loan, gold transfer).

This cog is mostly a command layer:
- Validates user input and business rules
- Delegates data mutations to service functions

Contains a small UI flow for starter loan terms:
- /loan shows an embed with terms
- user clicks "Accept Terms"
- modal requires typing CONFIRM exactly
"""

import logging

import discord
from discord import ui
from discord.ext import commands

from domain.guild.commands_policies import non_spam_command
from services.economy_services import add_gold, remove_gold
from services.friendship_services import add_friendship
from services.loan_services import (
    check_starter_loan_given,
    issue_loan,
    repay_loan,
)
from services.response_services import create_response
from services.users_services import is_user
from utils.custom_errors import VeyraError
from utils.emotes import GOLD_EMOJI
from utils.embeds.leaderboard.leaderboardembed import gold_leaderboard_embed
from utils.embeds.loanembed import build_loan_terms_embed

logger = logging.getLogger(__name__)


class Economy(commands.Cog):
    """Economy commands: leaderboard, starter loan, transfer."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # -----------------------------
    # Leaderboard
    # -----------------------------
    @commands.slash_command(description="Show the richest players leaderboard.")
    @commands.cooldown(1, 120, commands.BucketType.user)
    @non_spam_command()
    async def leaderboard(self, ctx: discord.ApplicationContext):
        """Display the gold leaderboard."""
        embed = await gold_leaderboard_embed(self.bot)
        await ctx.respond(embed=embed)

    # -----------------------------
    # Starter Loan UI
    # -----------------------------
    class StarterLoanTermsView(ui.View):
        """View containing the 'Accept Terms' button for starter loan."""

        def __init__(self, cog: "Economy"):
            super().__init__(timeout=60)
            self.cog = cog

        @ui.button(label="Accept Terms", style=discord.ButtonStyle.green)
        async def accept_terms(self, button: ui.Button, interaction: discord.Interaction):
            """Launch confirmation modal after user accepts terms."""
            # Open the confirmation modal
            await interaction.response.send_modal(Economy.StarterLoanModal(self.cog))

    class StarterLoanModal(ui.Modal):
        """Modal asking user to type CONFIRM to receive starter loan."""

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
            """Handle modal submission."""
            value = (self.confirm.value or "").strip()
            if value != "CONFIRM":
                await interaction.response.send_message(
                    "Loan cancelled. Type **CONFIRM** exactly if you want the starter loan.",
                    ephemeral=True,
                )
                return

            # Grant starter loan
            principal = 2000
            term_days = 7

            # Add gold first (existing behavior).
            new_balance, _ = add_gold(interaction.user.id, principal)

            # Issue loan record (starter pack loan id "0").
            ok, _, _ = issue_loan(interaction.user.id, "0")
            if ok:
                await interaction.response.send_message(
                    f"✅ Loan Granted!**\n\n"
                    f"You received **{principal}{GOLD_EMOJI}**.\n"
                    f"Repay within **{term_days} days** (no interest).\n"
                    f"Failing to repay will **hurt your credit score** and you'll be **locked out of loans**.\n\n"
                    f"Your new balance: **{new_balance}{GOLD_EMOJI}**",
                    ephemeral=True,
                )
                return

            # Preserve exact original response text/visibility.
            await interaction.response.send_message("You already have an active loan")

    # -----------------------------
    # Loan commands
    # -----------------------------
    @commands.slash_command(name="loan", description="Take a one-time starter loan.")
    @non_spam_command()
    async def loan(self, ctx: discord.ApplicationContext):
        """Take a starter pack loan (one-time). Shows terms before confirmation."""
        # todo: this shit basic af only for starter loan later when adding more loan types check credit score and stuff

        if check_starter_loan_given(ctx.author.id):
            await ctx.respond("You already took your one time loan")
            return

        embed = build_loan_terms_embed()
        view = self.StarterLoanTermsView(self)
        await ctx.respond(embed=embed, view=view)

    @commands.command()
    async def repayloan(self, ctx: commands.Context):
        """Legacy prefix command to repay current loan."""
        result = repay_loan(ctx.author.id)
        await ctx.send(result)

    # -----------------------------
    # Gold transfer
    # -----------------------------
    @commands.slash_command(description="Transfer gold to another user (5% fee).")
    @non_spam_command()
    async def transfer_gold(self, ctx: discord.ApplicationContext, target_user: discord.Member, amount: int):
        """Transfer gold from your wallet to another user. There is a 5% fee."""

        # Special case: donating gold to the bot.
        if target_user.id == self.bot.user.id:
            response = create_response("transfer_gold", 2, user=ctx.author.display_name)
            await ctx.respond(response)

            remove_gold(ctx.author.id, amount)
            logger.info(
                "Gold was given to Veyra",
                extra={
                    "user": ctx.author.name,
                    "flex": f"Gold amount: {amount}",
                    "cmd": "transfer_gold",
                },
            )

            # Friendship gains for donating.
            if amount >= 10:
                friendship_gain = amount // 10  # 1 EXP per 10 gold
                add_friendship(ctx.author.id, friendship_gain)

            add_friendship(ctx.author.id, 1)
            return

        # Target must exist in the system.
        if not is_user(target_user.id):
            await ctx.respond(
                "They are not my friend. They don't even have a wallet where am I supposed to send this money to? "
                f"Hmm <@{ctx.author.id}> ??"
            )
            return

        if amount <= 0:
            await ctx.respond("Atleast send 1 gold come on", ephemeral=True)
            return

        # No self-transfer.
        if target_user.id == ctx.author.id:
            response = create_response("transfer_gold", 1)
            await ctx.respond(response)
            return

        try:
            # Existing behavior: compute 95% and then remove/add that amount.
            new_amount = int(amount * 0.95)  # calculating 5% of total amount

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
                    "cmd": "transfer_gold",
                },
            )
        except VeyraError as e:
            # TODO: Use procedural error response
            await ctx.respond(str(e))


def setup(bot: commands.Bot):
    """Discord.py extension entrypoint."""
    bot.add_cog(Economy(bot))