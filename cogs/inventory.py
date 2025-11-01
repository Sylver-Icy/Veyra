"""
Inventory Cog for managing user inventories in the Discord bot.

This cog provides commands to transfer items between users, check a user's inventory,
and get detailed information about specific items. It handles item name resolution,
suggestions for mistyped item names, and logging of important actions.

Commands:
- /transfer_item: Transfer items from the command invoker to another user or the bot.
- !checkinventory: Display the inventory of the command invoker.
- !info: Get detailed information about a specified item.
"""

import logging

import discord
from discord.ext import commands, pages

from services.inventory_services import (
    transfer_item as transfer_item_service,
    take_item,
    get_inventory,
    get_item_details
)
from services.users_services import is_user
from services.response_services import create_response
from utils.itemname_to_id import get_item_id_safe

logger = logging.getLogger(__name__)


class Inventory(commands.Cog):
    """
    Cog for inventory management commands.

    Provides commands to transfer items, check inventories, and get item details.
    """

    def __init__(self, bot):
        self.bot = bot


    @commands.slash_command()
    async def transfer_item(self, ctx, target: discord.Member, item_name: str, amount: int):
        """
        Transfer your items to another user or the bot.

        Parameters:
        - ctx: The context of the command invocation.
        - target: The Discord member to transfer items to.
        - item_name: The name of the item to transfer.
        - amount: The quantity of the item to transfer.
        """
        if not is_user(target.id):
            await ctx.respond(f"Umm sorry {ctx.author.name}, they're not frnds with me. Can't interact")
            return
        # Convert item name to ID and get suggestions if not found
        item_id, suggestions = get_item_id_safe(item_name)

        # Suggest similar items if user typo’d the item name
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
            # No close matches found
            await ctx.respond("Bruh there is no such item not even close. Perhaps you meant: **Skill Issue**")
            return

        # Handle transfer if the target is the bot itself
        if target.id == self.bot.user.id:
            try:
                take_item(ctx.author.id, item_id, amount)
                response = create_response("transfer_item", 2, user=ctx.author.display_name, item=item_name)
                await ctx.respond(response)
                logger.info("%s was given to the bot", item_name, extra={"user": ctx.author.name, "flex": f"amount: {amount}", "cmd": "transfer_item"})

            except Exception as e:
                # Catch any VeyraError or other exceptions related to transfer
                await ctx.respond(str(e))

        # Handle case where user tries to transfer items to themselves
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
                    "Items tranferred to %s", target.name,
                    extra={
                        "user": ctx.author.name,
                        "flex": f"Item name and quantity: {item_name}|{amount}",
                        "cmd": "transfer_item"
                    }
                )
            except Exception as e:
                await ctx.respond(str(e))

    @commands.command()
    @commands.cooldown(1,15,commands.BucketType.user)
    async def checkinventory(self, ctx):
        """
        Check your own inventory (prefix command).

        Parameters:
        - ctx: The context of the command invocation.
        """
        status, embed_pages = get_inventory(ctx.author.id, ctx.author.name)

        if status == "start_event":
            # User has no items; send a friendly message
            await ctx.send("Awww you poor thing it seems you don't own anything. Here, take this flower from me :3")
        else:
            # Paginate and send inventory embeds
            paginator = pages.Paginator(pages=embed_pages)
            await paginator.send(ctx)

    @commands.command()
    @commands.cooldown(1,5,commands.BucketType.user)
    async def info(self, ctx, *, item_name: str):
        """
        Get detailed information about a specific item.

        Parameters:
        - ctx: The context of the command invocation.
        - item_name: The name of the item to get information about.
        """
        # Convert item name to ID and get suggestions if not found
        item_id, suggestions = get_item_id_safe(item_name)
        if suggestions:
            # Inform user about possible intended item if no exact match
            await ctx.send(f"There is no such item as {item_name} perhaps you meant {suggestions[0]}")
            return
        embed = get_item_details(item_id)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Inventory(bot))