"""profile.py

Profile + onboarding commands.

This cog covers:
- `!helloVeyra`: register user and start PvP onboarding
- `/help`: show help embed UI
- `/commandhelp`: show info about a specific command
- `/details`: show JSON-backed docs pages (topic based)
- `/introduction`: opens intro modal
- `/profile`: shows user profile embed with pagination

This file intentionally stays as a command/UI layer. Business logic lives in
`services/*`.
"""

import discord

from discord.ext import commands

from services.friendship_services import check_friendship
from services.inventory_services import give_item
from services.jobs_services import JobsClass
from services.response_services import create_response
from services.users_services import add_user, get_user_profile_new, is_user
from services.refferal_services import get_referral_card_data
from services.battle.tutorial_battle_services import start_tutorial_battle
from services.tutorial_services import TutorialState, get_tutorial_state

from domain.guild.commands_policies import non_spam_command


from utils.embeds.help.helpembed import (
    get_command_info_embed,
    get_all_commandhelp_options,
    get_help_embed,
    get_json_pages_embed,
)
from utils.embeds.profileembed import ProfilePagerView, build_profile_embed_page_1
from utils.embeds.refferalembed import build_referral_card

from utils.models.intromodel import create_intro_modal


def _commandhelp_autocomplete(ctx: discord.AutocompleteContext):
    query = (ctx.value or "").lower().strip()
    options = get_all_commandhelp_options()
    if query:
        options = [opt for opt in options if query in opt.lower()]
    return options[:25]


class Profile(commands.Cog):
    """User profile + onboarding commands."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    @non_spam_command()
    async def helloVeyra(self, ctx: commands.Context):
        """Register a user and start the PvP onboarding duel."""

        user_id = ctx.author.id
        user_name = ctx.author.name

        if is_user(user_id):
            state = await get_tutorial_state(user_id)
            if state != TutorialState.COMPLETED:
                await start_tutorial_battle(ctx, ctx.author)
                return

            try:
                title, progress = check_friendship(user_id)
            except Exception:
                # Keep the command usable even if an old friendship row is in a
                # bad state; default to a safe baseline instead of crashing.
                title, progress = "Stranger", 0.0

            if title == "Veyra's favourite 💖":
                response = create_response(
                    "friendship_check", 4, user=user_name, title=title, progress=progress
                )
            elif title in ("Stranger", "Acquaintance", "Casual"):
                response = create_response(
                    "friendship_check", 1, user=user_name, title=title, progress=progress
                )
            elif title in ("Friend", "Close Friend"):
                response = create_response(
                    "friendship_check", 2, user=user_name, title=title, progress=progress
                )
            else:
                response = create_response(
                    "friendship_check", 3, user=user_name, title=title, progress=progress
                )

            await ctx.send(response)
            return

        if not add_user(user_id, user_name):
            await ctx.send("Something broke while making your profile. Try `!helloVeyra` again.")
            return

        give_item(user_id, 183, 2, True)
        user = JobsClass(user_id)
        user.gain_energy(150)

        await ctx.send(
            "Oh, you wanna say hello?\n"
            "Let's see if you can fight first."
        )
        await start_tutorial_battle(ctx, ctx.author)

    # -----------------------------
    # Help / Docs
    # -----------------------------
    @commands.slash_command(description="Show the help menu.")
    @commands.cooldown(1, 25, commands.BucketType.user)
    @non_spam_command()
    async def help(self, ctx):
        """Show help embed + interactive view."""
        embed, view = get_help_embed(ctx.author)
        await ctx.respond(embed=embed, view=view)

    @commands.slash_command(description="Get detailed help for a specific command.")
    @commands.cooldown(1, 5, commands.BucketType.user)
    @non_spam_command()
    @discord.option(
        "command_name",
        description="Choose a command",
        required=True,
        autocomplete=discord.utils.basic_autocomplete(_commandhelp_autocomplete),
    )
    async def commandhelp(self, ctx: discord.ApplicationContext, command_name: str):
        """Slash helper for command documentation."""
        embed = get_command_info_embed(command_name)
        await ctx.respond(embed=embed)

    @commands.slash_command(description="Show feature details for a topic.")
    @discord.option(
        "topic",
        description="Choose a help topic",
        required=True,
        choices=[
            "Battle",
            "Quests",
            "Jobs",
            "Loadout",
            "Race",
            "Smelting",
            "Inventory",
            "Gambling",
            "Loan",
            "Alchemy",
            "Potions"
        ]
    )
    async def details(self, ctx: discord.ApplicationContext, topic: str):
        """Show feature docs pages for a topic."""
        embed, view = get_json_pages_embed(ctx.author, topic.lower())
        msg = await ctx.respond(embed=embed, view=view)

        if view:
            view.message = msg

    # -----------------------------
    # Introduction
    # -----------------------------
    @commands.slash_command(description="Introduce yourself to the server.")
    @non_spam_command()
    async def introduction(self, ctx):
        """Open the introduction modal."""
        modal = create_intro_modal(ctx.author)
        await ctx.send_modal(modal)

    # -----------------------------
    # Profile
    # -----------------------------
    @commands.slash_command(description="View your profile.")
    @commands.cooldown(1, 250, commands.BucketType.user)
    @non_spam_command()
    async def profile(self, ctx):
        """Show the user's profile with pagination."""
        profile = get_user_profile_new(ctx.author.id)
        view = ProfilePagerView(profile=profile, author_id=ctx.author.id)
        await ctx.respond(embed=build_profile_embed_page_1(profile), view=view)


    @commands.slash_command(description="Track your invites and rewards")
    @commands.cooldown(1, 250, commands.BucketType.user)
    @non_spam_command()
    async def invite(self, ctx):
        user_id = ctx.author.id
        username = ctx.author.name

        data = get_referral_card_data(user_id)

        embed = build_referral_card(
            username=username,
            total_invites=data["total_invites"],
            successful_invites=data["successful_invites"],
            current_milestone=data["current_milestone"],
            next_milestone=data["next_milestone"],
            next_reward_name=data["next_reward_name"],
        )

        await ctx.respond(embed=embed)

def setup(bot: commands.Bot):
    """Discord.py extension entrypoint."""
    bot.add_cog(Profile(bot))
