import logging

import discord
from discord.ext import commands, pages
from discord import Option  # pylint: disable=no-name-in-module

from services.inventory_services import (
    add_item as add_item_service,
    give_item as give_item_service,
    transfer_item as transfer_item_service,
    take_item,
    get_inventory,
    get_item_details
)
from services.users_services import is_user
from services.response_services import create_response
from utils.custom_errors import WrongItemError, VeyraError
from utils.itemname_to_id import get_item_id_safe

logger = logging.getLogger(__name__)


class Inventory(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command()
    async def add_item(
        self,
        ctx,
        item_name: str,
        item_description: str,
        item_price: int,
        item_rarity: str = Option(
            str,
            choices=["Common", "Rare", "Epic", "Legendary", "Paragon", "Lootbox"],
            description="Select the rarity of the item",
        ),
        item_id: int = None,
        item_icon: str = None,
        item_durability: int = None,
    ):
        """Add a new item to the database."""
        # TODO: Add proper error handling + logging everywhere, not just here

        if add_item_service(item_id, item_name, item_description, item_price, item_rarity, item_icon, item_durability):
            await ctx.respond("❌ This item already exists.")
        else:
            await ctx.respond(
                f"{ctx.author.mention} added a **{item_rarity}** item called **{item_name}-{item_id}**.\n"
                f'Description: "{item_description}"'
            )
            logger.info("%s added %s to database", ctx.author.name, item_name, extra={"cmd": "add_item"})

    @commands.slash_command()
    async def give_item(self, ctx, target: discord.Member, item_name: str, amount: int):
        """Give an item to another user."""
        # Convert the item name to ID
        item_id, suggestions = get_item_id_safe(item_name)

        # Suggest similar items if user typo’d
        if not item_id:
            if suggestions:
                logger.info("Items suggested for %s", item_name, extra={"user": ctx.author.name, "flex": f"suggested items {suggestions}", "cmd": "give_item"})
                if len(suggestions) == 1:
                    await ctx.respond(
                        f"There is no such item as `{item_name}`, perhaps you meant {suggestions[0]}?"
                    )
                elif len(suggestions) == 2:
                    await ctx.respond(
                        f"There is no such item as `{item_name}`, perhaps you meant {suggestions[0]}? "
                        f"or maybe {suggestions[1]}??"
                    )
                else:
                    await ctx.respond(
                        f"There is no such item as `{item_name}`. Did you mean one of these? {suggestions}"
                    )
                return
            await ctx.respond("Bruh there is no such item not even close. Perhaps you meant: **Skill Issue**")
            logger.info("No matching item found for %s", item_name)
            return

        # If someone tries to send items to the bot
        if target.id == self.bot.user.id:
            await ctx.respond("Uhmm I dunno where to keep that but hey Thanks!!!!")
            logger.info("%s was given to the bot", item_name, extra={"user": ctx.author.name, "flex": f"amount: {amount}", "cmd": "give_item"})
            return

        # If someone tries to send items to an unregistered user
        if not is_user(target.id):
            await ctx.respond("Can't send items to unregistered users")
            return

        try:
            give_item_service(target.id, item_id, amount)
            # TODO: Switch to procedural response once ready
            await ctx.respond(f"{ctx.author.mention} gave {amount}x {item_name.capitalize()} to {target.mention}")
            logger.info(
                "Items tranferred to %s",target.name,
                extra={"user": ctx.author.name,
                "flex": f"Item name and quantity: {item_name}|{amount}",
                "cmd": "give_item"}
                )
        except WrongItemError as e:
            await ctx.respond(str(e))

    @commands.slash_command()
    async def transfer_item(self, ctx, target: discord.Member, item_name: str, amount: int):
        """Transfer your items to another user."""
        # Convert item name to ID
        item_id, suggestions = get_item_id_safe(item_name)

        # Suggest similar items if user typo’d
        if not item_id:
            if suggestions:
                if len(suggestions) == 1:
                    await ctx.respond(
                        f"There is no such item as `{item_name}`, perhaps you meant {suggestions[0]}?"
                    )
                elif len(suggestions) == 2:
                    await ctx.respond(
                        f"There is no such item as `{item_name}`, perhaps you meant {suggestions[0]}? "
                        f"or maybe {suggestions[1]}??"
                    )
                else:
                    await ctx.respond(
                        f"There is no such item as `{item_name}`. Did you mean one of these? {suggestions}"
                    )
                return
            await ctx.respond("Bruh there is no such item not even close. Perhaps you meant: **Skill Issue**")
            return

        # If the target is the bot
        if target.id == self.bot.user.id:
            try:
                take_item(ctx.author.id, item_id, amount)
                response = create_response("transfer_item", 2, user=ctx.author.display_name, item=item_name)
                await ctx.respond(response)
                logger.info("%s was given to the bot", item_name, extra={"user": ctx.author.name, "flex": f"amount: {amount}", "cmd": "transfer_item"})

            except VeyraError as e:
                await ctx.respond(str(e))

        # If target is the user themselves
        elif target.id == ctx.author.id:
            response = create_response("transfer_item", 1, user=ctx.author.display_name, item=item_name)
            await ctx.respond(response)

        # Normal transfer to another user
        else:
            try:
                transfer_item_service(ctx.author.id, target.id, item_id, amount)
                response = create_response(
                    "transfer_item",
                    3,
                    user=ctx.author.mention,
                    target=target.mention,
                    item=item_name,
                    amount=amount,
                )
                await ctx.respond(response)
                logger.info(
                "Items tranferred to %s",target.name,
                extra={"user": ctx.author.name,
                "flex": f"Item name and quantity: {item_name}|{amount}",
                "cmd": "transfer_item"}
                )
            except VeyraError as e:
                await ctx.respond(str(e))

    @commands.command()
    # @commands.cooldown(1,15,commands.BucketType.user)
    async def checkinventory(self, ctx):
        """Check your own inventory (prefix command)."""
        status, embed_pages = get_inventory(ctx.author.id, ctx.author.name)

        if status == "start_event":
            await ctx.send("Awww you poor thing it seems you don't own anything. Here, take this flower from me :3")
        else:
            paginator = pages.Paginator(pages=embed_pages)
            await paginator.send(ctx)

    @commands.command()
    # @commands.cooldown(1,15,commands.BucketType.user)
    async def info(self, ctx, *, item_name: str):
       id,suggestions = get_item_id_safe(item_name)
       if suggestions:
           await ctx.send(f"There is no such item as {item_name} perhaps you meant {suggestions[0]}")
           return
       embed = get_item_details(id)
       await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Inventory(bot))