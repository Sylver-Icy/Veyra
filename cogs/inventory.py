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
    get_item_details,
    use_item
)
from services.users_services import is_user
from services.response_services import create_response
from services.friendship_services import add_friendship
from services.delievry_minigame_services import lookup_item_sources

from utils.itemname_to_id import get_item_id_safe
from utils.custom_errors import NotEnoughItemError

logger = logging.getLogger(__name__)


class Inventory(commands.Cog):
    """
    Cog for inventory management commands.

    Provides commands to transfer items, check inventories, and get item details.
    """

    def __init__(self, bot):
        self.bot = bot


    @commands.slash_command(description = "Tranfer any item from your inventory to another user")
    async def transfer_item(self, ctx, target: discord.Member, item_name: str, amount: int):
        """
        Transfer your items to another user or the bot.

        Parameters:
        - ctx: The context of the command invocation.
        - target: The Discord member to transfer items to.
        - item_name: The name of the item to transfer.
        - amount: The quantity of the item to transfer.
        """
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

                add_friendship(ctx.author.id, 9*amount)

                response = create_response("transfer_item", 2, user=ctx.author.display_name, item=item_name)
                await ctx.respond(response)
                logger.info("%s was given to the bot", item_name, extra={"user": ctx.author.name, "flex": f"amount: {amount}", "cmd": "transfer_item"})
                return

            except Exception as e:
                # Catch any VeyraError or other exceptions related to transfer
                await ctx.respond(str(e))
                return

        if not is_user(target.id):
            await ctx.respond(f"Umm sorry {ctx.author.name}, they're not frnds with me. Can't interact")
            return
        # Handle case where user tries to transfer items to themselves
        elif target.id == ctx.author.id:
            response = create_response("transfer_item", 1, user=ctx.author.display_name, item=item_name)
            await ctx.respond(response)

        # Normal transfer to another user
        else:
            try:
                result = transfer_item_service(ctx.author.id, target.id, item_id, amount)
                if result == "full_inventory":
                    await ctx.respond("Reciever has no space to recieve this")
                    return

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


    @commands.slash_command(description="Find where any item can be obtained currently for only 25G")
    async def find_item(self, ctx, item_name: str):
        """
        Find possible sources of an item (shop, marketplace, or players).
        """
        info = lookup_item_sources(ctx.author.id, item_name)
        await ctx.respond(info["message"], allowed_mentions=discord.AllowedMentions.none())


    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def info(self, ctx, *, item_name: str):
        """
        Get detailed information about a specific item.

        Parameters:
        - ctx: The context of the command invocation.
        - item_name: The name of the item to get information about.
        """
        item_id, suggestions = get_item_id_safe(item_name)

        # Case 1: item not found, but suggestions exist
        if item_id is None and suggestions:
            await ctx.send(f"There is no such item as **{item_name}**, perhaps you meant **{suggestions[0]}**?")
            return

        # Case 2: item not found, no suggestions at all
        if item_id is None and not suggestions:
            await ctx.send("Idk about anything like that.")
            return

        # Case 3: item found successfully
        embed = get_item_details(ctx.author.id, item_id)
        if embed is None:
            await ctx.send("No such item.")
            return

        await ctx.send(embed=embed)


    @commands.command()
    async def use(self, ctx, *, item_name: str):
        lootboxes = ("wooden box", "iron box", "stone box", "platinum box")
        if item_name.lower() in lootboxes:
            await ctx.send(f"What are you tryna use it for??? you gonna eat it??\n use `!open {item_name.lower()}` to open that thing Einstein")
            return
        item_id, sugestions = get_item_id_safe(item_name)
        if item_id:
            try:
                result = use_item(ctx.author.id, item_id)
                await ctx.send(result)
                return
            except NotEnoughItemError:
                await ctx.send (f"You don't have any {item_name.capitalize()}. Can't use!")
                return

        if sugestions != []:
            await ctx.send(f"Hmmm there is no such item as {item_name}? Ig you meant {sugestions[0]}?")
            return

        await ctx.send("Hmm how can one use something which doesn't even exist?" )

def setup(bot):
    bot.add_cog(Inventory(bot))