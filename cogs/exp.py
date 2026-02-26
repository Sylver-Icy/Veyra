import time
import random
import discord

from discord.ext import commands, pages

from services.exp_services import current_exp
from services.economy_services import check_wallet_full
from services.inventory_services import get_inventory
from services.jobs_services import JobsClass
from services.response_services import create_response
from services.friendship_services import add_friendship
from services.upgrade_services import building_lvl
from domain.buildings.building_descriptions import get_building_description

from utils.emotes import GOLD_EMOJI, CHIP_EMOJI
from utils.chatexp import add_exp_with_announcement


user_cooldowns = {}

class Exp(commands.Cog):
    check = discord.SlashCommandGroup("check", "Check various stats")

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
        await add_exp_with_announcement(ctx, user_id, random.randint(1,20))


    @check.command(name="wallet", description="Check your wallet")
    async def check_wallet(self, ctx: discord.ApplicationContext):
        gold, chip = check_wallet_full(ctx.author.id)
        response = create_response(
            "check_wallet",
            1,
            user=ctx.author.mention,
            gold=gold,
            emoji=GOLD_EMOJI
        )
        await ctx.respond(f"{response}\nChips Available: {chip}{CHIP_EMOJI}")

    @check.command(name="energy", description="Check your energy")
    async def check_energy(self, ctx: discord.ApplicationContext):
        user = JobsClass(ctx.author.id)
        energy = user.check_energy()
        await ctx.respond(f"You current have {energy} energy...")

    @check.command(name="inventory", description="Check your inventory")
    @discord.option(
        "category",
        description="Filter inventory by category",
        required=False,
        choices=["Common", "Rare", "Epic", "Legendary", "minerals", "lootbox", "Potion"]
    )
    async def check_inventory(self, ctx: discord.ApplicationContext, category: str = None):
        status, embed_pages = get_inventory(ctx.author.id, ctx.author.name, category)

        if status == "start_event":
            return await ctx.respond(
                "Awww you poor thing… you don't own anything.\nHere, take this flower from me :3"
            )

        paginator = pages.Paginator(pages=embed_pages)
        return await paginator.respond(ctx.interaction)

    @check.command(name="exp", description="Check your EXP and level")
    async def check_exp_cmd(self, ctx: discord.ApplicationContext):
        exp, level = current_exp(ctx.author.id)
        response = create_response(
            "check_exp",
            1,
            user=ctx.author.mention,
            level=level,
            exp=exp
        )
        return await ctx.respond(response)

    @check.command(name="smelter", description="Check your smelter level")
    async def check_smelter(self, ctx: discord.ApplicationContext):
        lvl = building_lvl(ctx.author.id, "smelter")
        desc = get_building_description("smelter", lvl)
        return await ctx.respond(desc)

    @check.command(name="brewing_stand", description="Check your brewing stand level")
    async def check_brewing(self, ctx: discord.ApplicationContext):
        lvl = building_lvl(ctx.author.id, "brewing stand")
        desc = get_building_description("brewing stand", lvl)
        return await ctx.respond(desc)

    @check.command(name="pockets", description="Check your pockets & inventory level")
    async def check_pockets(self, ctx: discord.ApplicationContext):
        inv_lvl = building_lvl(ctx.author.id, "inventory")
        pocket_lvl = building_lvl(ctx.author.id, "pockets")

        inv_desc = get_building_description("inventory", inv_lvl)
        pocket_desc = get_building_description("pockets", pocket_lvl)

        return await ctx.respond(f"{inv_desc}\n{pocket_desc}")

    @check.command(name="status", description="Check active effects and strain")
    async def check_status(self, ctx: discord.ApplicationContext):
        from database.sessionmaker import Session
        from services.alchemy_services import get_active_user_effect, get_strain_status

        with Session() as session:
            effect = get_active_user_effect(session, ctx.author.id)
            strain_msg = get_strain_status(session, ctx.author.id)

        effect_display = effect if effect else "None"

        return await ctx.respond(
            f"**Active Effect:** {effect_display}\n"
            f"**Strain:** {strain_msg}"
        )


def setup(bot):
    bot.add_cog(Exp(bot))