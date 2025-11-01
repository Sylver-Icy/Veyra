import logging
from discord.ext import commands, pages
from discord.commands import Option

from services.marketplace_services import create_listing, load_marketplace, buy_listed_item
from utils.itemname_to_id import get_item_id_safe

logger = logging.getLogger(__name__)

class Marketplace(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.slash_command()
    @commands.cooldown(2,3600,commands.BucketType.user)
    async def create_listing(
        self,
        ctx,
        item_name = Option(str, "Name of the item you want to list"),
        quantity = Option(int, "Number of items to list"),
        price = Option(int, "Cost for each item", min_value=0, max_value=9999)
    ):
        """
        Create a marketplace listing for a given item name, quantity, and price.

        The item(s) will be taken from your inventory and held in escrow.
        """
        # Validate price and quantity
        if price < 0:
            await ctx.respond("Hmm, you can give freebies, but negative prices? Not allowed.")
            return

        if quantity < 1:
            await ctx.respond("You need to list at least 1 item.")
            return

        # Resolve item name to ID
        item_id, suggestions = get_item_id_safe(item_name)

        # Suggest corrections if item is invalid
        if suggestions:
            suggestion_str = ', '.join(suggestions)
            await ctx.respond(f"Hmm, I couldn't find that item. Did you mean: {suggestion_str}?")
            return

        # Create the listing
        listing_id = create_listing(ctx.author.id, item_id, quantity, price)

        if listing_id > 0:
            await ctx.respond(
                f"Hi, your listing of {quantity}x {item_name.capitalize()} @ {price} per unit is online with ID → `{listing_id}`"
            )
            logger.info("Market Place listing was created", extra={
                "user": ctx.author.name,
                "flex": f"item_name {item_name} | amount {quantity}",
                "cmd": "create listing"
            })
        else:
            await ctx.respond("You don't own enough items to create that listing. Maybe try selling fewer items?")


    @commands.slash_command()
    @commands.cooldown(1,15,commands.BucketType.user)
    async def loadmarketplace(self, ctx):
        """
        Display all active listings in the marketplace.
        """
        embed_pages = load_marketplace()
        paginator = pages.Paginator(pages=embed_pages)
        await paginator.respond(ctx.interaction)


    @commands.slash_command()
    @commands.cooldown(1,5,commands.BucketType.user)
    async def buy_from_marketplace(self, ctx, listing_id: int, quantity: int):
        """
        Buy any  item from a marketplace listing using the ID.
        """
        response = buy_listed_item(ctx.author.id, listing_id, quantity)
        await ctx.respond(response)


# ──────────────────────────────────────────────────────────────
# Cog setup function
# ──────────────────────────────────────────────────────────────

def setup(bot):
    bot.add_cog(Marketplace(bot))
