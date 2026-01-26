"""profile.py

Profile + onboarding commands.

This cog covers:
- `!helloVeyra`: classic prefix onboarding flow (register user)
- `/help`: show help embed UI
- `!commandhelp`: show info about a specific command
- `!details`: show JSON-backed docs pages (topic based)
- `/introduction`: opens intro modal
- `/profile`: shows user profile embed with pagination

This file intentionally stays as a command/UI layer. Business logic lives in
`services/*`.
"""

import asyncio

from discord.ext import commands

from services.friendship_services import check_friendship
from services.inventory_services import give_item
from services.jobs_services import JobsClass
from services.response_services import create_response
from services.users_services import add_user, get_user_profile_new, is_user
from services.refferal_services import get_referral_card_data

from domain.guild.commands_policies import non_spam_command


from utils.embeds.help.helpembed import (
    get_command_info_embed,
    get_help_embed,
    get_json_pages_embed,
)
from utils.embeds.profileembed import ProfilePagerView, build_profile_embed_page_1
from utils.embeds.refferalembed import build_referral_card

from utils.models.intromodel import create_intro_modal


class Profile(commands.Cog):
    """User profile + onboarding commands."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        # Tracks users currently mid-registration to avoid duplicate flows.
        self.users_pending: set[int] = set()

    @commands.command()
    @commands.cooldown(1, 15, commands.BucketType.user)
    @non_spam_command()
    async def helloVeyra(self, ctx: commands.Context):
        """Register a user in the database.

        Flow:
        - If already registered: respond with friendship status.
        - If new: ask Yes/No, wait up to 30 seconds.
            - Yes: register, give starter items + energy.
            - No: (well...) insult.
        """

        user_id = ctx.author.id
        user_name = ctx.author.name

        # Already registered user
        if is_user(user_id):
            title, progress = check_friendship(user_id)

            if title in ("Stranger", "Acquaintance", "Casual"):
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

        # New user registration
        if user_id in self.users_pending:
            await ctx.send(
                "You haven't replied to me my previous message. YOU WANNA BE FRIEND WITH ME OR NOT."
            )
            return

        self.users_pending.add(user_id)
        await ctx.send("Hy there wanna be frnds with me? (Yes/No)")

        # Checks if the message is from the same user, same channel, and in allowed form.
        def check(m):
            return (
                m.author == ctx.author
                and m.channel == ctx.channel
                and m.content.lower() in ["yes", "no"]
            )

        try:
            # 30 sec wait time for user to respond
            msg = await self.bot.wait_for("message", timeout=30, check=check)

            if msg.content.lower() == "yes":
                await ctx.send(
                    "Yay! Here keep these bags of gold as a gift for our new friendship ^^\n"
                    " OH!! and also why don't you use `/introduction` and introduce yourself to everyone"
                )
                add_user(user_id, user_name)
                give_item(user_id, 183, 2, True)
                self.users_pending.remove(user_id)

                # Starter energy reward
                user = JobsClass(user_id)
                user.gain_energy(150)  # give 150 energy on registration

            else:
                self.users_pending.remove(user_id)
                await ctx.send("Go fuck yourself 😇")

        except asyncio.TimeoutError:
            # If user didn't reply in 30 sec let them know command ended
            self.users_pending.remove(user_id)
            await ctx.send(f"Too slow ig you don't wanna be frnds {user_name}")

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

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @non_spam_command()
    async def commandhelp(self, ctx: commands.Context, *, command_name):
        """Prefix helper for command documentation."""
        embed = get_command_info_embed(command_name)
        await ctx.send(embed=embed)

    @commands.command()
    async def details(self, ctx: commands.Context, topic):
        """Show feature docs pages for a topic."""
        embed, view = get_json_pages_embed(ctx.author, topic.lower())
        msg = await ctx.send(embed=embed, view=view)

        # Some views need message reference for interaction callbacks.
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
