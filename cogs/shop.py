"""shop.py

Shop + casino commands.

Commands in this cog:
- `!buy`: Buy items from bot shop
- `!sell`: Sell items to bot shop
- `!buychips`: Buy casino chips (chip packs)
- `!cashout`: Convert chips back to gold
- `/shop`: Show today's daily shop (embed + view)
- `/casino`: Show casino offers (chips + cashout)

This cog is intentionally thin and delegates business rules to services.
"""

import logging

from discord.ext import commands

from domain.casino.rules import CHIP_OFFERS, CONVERSION_RATES  # noqa: F401 (imported for future use)
from domain.guild.commands_policies import non_spam_command
from services.economy_services import add_gold
from services.shop_services import (
    buy_chips,
    buy_item,
    cashout_chips,
    daily_shop,
    get_today_cashout_offers,
    get_today_chip_offers,
    sell_item,
)
from services.inventory_services import take_item
from utils.custom_errors import NotEnoughItemError
from utils.embeds.casinoembed import get_casino_view_and_embed
from utils.itemname_to_id import get_item_id_safe

logger = logging.getLogger(__name__)


class Shop(commands.Cog):
    """Shop-related commands (shop, sell, casino)."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # -----------------------------
    # Prefix commands: shop buy/sell
    # -----------------------------
    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def buy(self, ctx: commands.Context, *args):
        """Buy items from the bot shop.

        Usage: !buy [item name] [quantity]
        """

        if len(args) < 2:
            await ctx.send("Usage: !buy [item name] [quantity]")
            return

        try:
            quantity = int(args[-1])
        except ValueError:
            await ctx.send("Quantity must be a number.")
            return

        item_name = " ".join(args[:-1]).lower()

        # Gets the item id if name matches; else suggests similar names in case of typo.
        item_id, suggestions = get_item_id_safe(item_name)
        if suggestions:
            await ctx.send(f"Item not found in database. I think you meant {suggestions[0]} ???")
            return

        response = buy_item(ctx.author.id, item_id, quantity)
        if response == "Purchase successful":
            await ctx.send(f"You bought {quantity} of {item_name.capitalize()}!!!")
            logger.info("%s bought %dX%s from bot", ctx.author.name, quantity, item_name)
        else:
            await ctx.send(response)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def sell(self, ctx: commands.Context, *args):
        """Sell items back to the bot shop.

        Usage: !sell [item name] [quantity]

        Note: Bars are handled here as a special case (fixed prices).
        """

        if len(args) < 2:
            await ctx.send("Usage: !sell [item name] [quantity]")
            return

        try:
            quantity = int(args[-1])
        except ValueError:
            await ctx.send("Quantity must be a number.")
            return

        item_name = " ".join(args[:-1]).lower()

        # Special-case minerals: handled directly here (legacy behavior).
        minerals = ("iron bar", "copper bar", "silver bar")

        if item_name.lower() in minerals:
            if item_name.lower() == "iron bar":
                try:
                    take_item(ctx.author.id, 190, quantity)
                except NotEnoughItemError:
                    await ctx.send(f"You don't have enough {item_name} to sell")
                    return
                price = 150

            elif item_name.lower() == "copper bar":
                try:
                    take_item(ctx.author.id, 189, quantity)
                except NotEnoughItemError:
                    await ctx.send(f"You don't have enough {item_name} to sell")
                    return
                price = 50

            else:
                try:
                    take_item(ctx.author.id, 191, quantity)
                except NotEnoughItemError:
                    await ctx.send(f"You don't have enough {item_name} to sell")
                    return
                price = 450

            revenue = price * quantity
            add_gold(ctx.author.id, revenue)
            await ctx.send(f"You sold {quantity} X {item_name.title()}!! Gold gained -> {revenue} ")
            return

        # gets the item id if name matches else suggests similar names in case of typo
        item_id, suggestions = get_item_id_safe(item_name)
        if suggestions:
            await ctx.send(f"Item not found in database. You meant {suggestions[0]} ???")
            return

        response = sell_item(ctx.author.id, item_id, quantity)
        await ctx.send(response)

    # -----------------------------
    # Prefix commands: casino chip offers
    # -----------------------------
    @commands.command()
    async def buychips(self, ctx: commands.Context, pack_id: str):
        """Buy chips using a predefined chip pack id."""
        result = buy_chips(ctx.author.id, pack_id)
        await ctx.send(result)

    @commands.command()
    async def cashout(self, ctx: commands.Context, pack_id: str):
        """Cash out chips back into gold using a predefined cashout pack id."""
        result = cashout_chips(ctx.author.id, pack_id)
        await ctx.send(result)

    # -----------------------------
    # Slash commands
    # -----------------------------
    @commands.slash_command(description="View today's shop offers.")
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def shop(self, ctx):
        """Show the daily shop embed."""
        embed, view = daily_shop()
        await ctx.respond(embed=embed, view=view)

    @commands.slash_command(description="Open the casino menu.")
    @commands.cooldown(1, 155, commands.BucketType.user)
    @non_spam_command()
    async def casino(self, ctx):
        """Show the casino view with today's chip + cashout offers."""
        # Placeholder packs (temporary)
        chip_offer = get_today_chip_offers()
        cashout_offer = get_today_cashout_offers()
        embed, view = get_casino_view_and_embed(chip_offer, cashout_offer)
        await ctx.respond(embed=embed, view=view)


def setup(bot: commands.Bot):
    """Discord.py extension entrypoint."""
    bot.add_cog(Shop(bot))