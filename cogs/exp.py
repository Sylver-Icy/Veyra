import time

from discord.ext import commands, pages

from services.exp_services import current_exp
from services.economy_services import check_wallet_full
from services.inventory_services import get_inventory
from services.jobs_services import JobsClass
from services.response_services import create_response
from services.friendship_services import add_friendship

from utils.emotes import GOLD_EMOJI, CHIP_EMOJI


user_cooldowns = {}

class Exp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        """Give EXP every time a command successfully runs."""
        if ctx.author.bot:
            return

        now = time.time()
        user_id = ctx.author.id

        # Prevent EXP farming
        if user_id in user_cooldowns and now - user_cooldowns[user_id] < 10:
            return  # 10s cooldown per user for EXP gain

        user_cooldowns[user_id] = now
        add_friendship(user_id, 1)


    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def check(self, ctx, value):
        """
        Check various stats using short keywords:
        wallet, energy, inventory, exp.
        """

        val = value.lower()

        # ──────────────────────────────
        # WALLET
        # ──────────────────────────────
        if val.startswith(("wal", "wall", "walle")):
            gold,chip = check_wallet_full(ctx.author.id)
            response = create_response("check_wallet", 1, user=ctx.author.mention, gold=gold, emoji=GOLD_EMOJI)
            await ctx.send(f"{response}\nChips Available: {chip}{CHIP_EMOJI}")
            return

        # ──────────────────────────────
        # ENERGY
        # ──────────────────────────────
        if val.startswith(("en", "ene")):
            user = JobsClass(ctx.author.id)
            energy = user.check_energy()
            await ctx.send(f"You current have {energy} energy...")
            return


        # ──────────────────────────────
        # INVENTORY
        # ──────────────────────────────
        if val.startswith(("inv", "inve")):

            #Check your own inventory (prefix command).

            status, embed_pages = get_inventory(ctx.author.id, ctx.author.name)

            if status == "start_event":
                # User has no items; send a friendly message
                return await ctx.send(
                    "Awww you poor thing… you don't own anything.\nHere, take this flower from me :3"
                )

            # Paginate and send inventory embeds
            paginator = pages.Paginator(pages=embed_pages)
            return await paginator.send(ctx)

        # ──────────────────────────────
        # EXP / LEVEL
        # ──────────────────────────────
        if val.startswith(("ex", "exp")):

            #Check  current EXP and level.

            exp, level = current_exp(ctx.author.id)
            response = create_response(
                "check_exp",
                1,
                user=ctx.author.mention,
                level=level,
                exp=exp
            )
            return await ctx.send(response)


def setup(bot):
    bot.add_cog(Exp(bot))