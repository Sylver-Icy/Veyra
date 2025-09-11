from discord.ext import commands
import discord
from discord import Option  # pylint: disable=no-name-in-module
import logging
from services.inventory_services import add_item as add_item_service, give_item as give_item_service, transfer_item, get_inventory
from services.users_services import is_user
from services.response_serives import create_response
from utils.custom_errors import WrongItemError, VeyraError
from utils.itemname_to_id import item_name_to_id,suggest_similar_item

logger = logging.getLogger(__name__)

class Inventory(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    @commands.slash_command()
    async def add_item(self,
                    ctx,
                    item_name: str,
                    item_description: str,
                    item_price: int,
                    item_rarity: str = Option(
                        str,
                        choices=["Common", "Rare", "Epic", "Legendary", "Paragon", "Lootbox"],
                        description="Select the rarity of item"
                    ),
                    item_id: int = None,
                    item_icon: str = None,
                    item_durability: int = None):
        """Adds an item to database"""

        if add_item_service(item_id, item_name, item_description, item_price, item_rarity, item_icon, item_durability):
            await ctx.respond("❌ This item already exists.")
        else:
            await ctx.respond(
                f"{ctx.author.mention} added a **{item_rarity}** item called **{item_name}-{item_id}**.\n"
                f'Description: "{item_description}"'
            )
            logger.info("%s added %s to database", ctx.author.name, item_name)

    @commands.slash_command()
    async def give_item(self,ctx,target: discord.Member, item_name: str, amount: int):
        """Slash command to give items to users"""
        #Convert the item_name to id
        item_id = item_name_to_id.get(item_name.lower())
        #Suggest items to  user if they made a typo
        if not item_id:
            suggestions = [s.title() for s in suggest_similar_item(item_name)]
            if suggestions:
                length = len(suggestions)
                if length == 1:
                    await ctx.respond(f"There is no such item as `{item_name}`, perhaps you meant {suggestions[0]} ?")
                    return
                elif length == 2:
                    await ctx.respond(f"There is no such item as `{item_name}`, perhaps you meant {suggestions[0]}? or maybe {suggestions[1]} ??")
                    return
                else:
                    await ctx. respond(f"There is no such item as `{item_name}`. Did you mean one these? {suggestions}")
                    return
            await ctx.respond("Bruh there is no such item not even close. Perhaps you meant: **Skill Issue**")
            return
        #If someone tries to send items to the bot
        if target.id ==  self.bot.user.id:
            await ctx.respond("Uhmm I dunno where to keep that but hey Thanks!!!!")
            return
        #if someone tries to send items to uneregistered user
        if not is_user(target.id):
            await ctx.respond ("Can't send items to unregistered users")
            return
        try:
            give_item_service(target.id, item_id, amount)
            await ctx.respond(f"{ctx.author.mention} gave {amount}X {item_name.capitalize()} to {target.mention}")
        except WrongItemError as e:
            await ctx.respond(e)

    @commands.slash_command()
    async def tranfer_item(self,ctx,target: discord.Member, item_name: str, amount:int):
        """
        Give your items to your friends!!
        """
        #convert item name to id
        item_id = item_name_to_id.get(item_name.lower())
        #Suggest items to  user if they made a typo
        if not item_id:
            suggestions = [s.title() for s in suggest_similar_item(item_name)]
            if suggestions:
                length = len(suggestions)
                if length == 1:
                    await ctx.respond(f"There is no such item as `{item_name}`, perhaps you meant {suggestions[0]} ?")
                    return
                elif length == 2:
                    await ctx.respond(f"There is no such item as `{item_name}`, perhaps you meant {suggestions[0]}? or maybe {suggestions[1]} ??")
                    return
                else:
                    await ctx. respond(f"There is no such item as `{item_name}`. Did you mean one these? {suggestions}")
                    return
            await ctx.respond("Bruh there is no such item not even close. Perhaps you meant: **Skill Issue**")
            return

        #If the target is bot
        if target.id == self.bot.user.id:
            #create response for the transfer_item use case with mood 1 here it means when bot is target
            response = create_response("transfer_item", 1, user=ctx.author.display_name, item_name=item_name)
            await ctx.respond(response)

        #if target is user themselves
        elif target.id == ctx.author.id:
            response = create_response("transfer_item",2, user=ctx.author.display_name, item_name=item_name)
            await ctx.respond(response)

        #if target is someone else (normal transfer)
        else:
            try:
                transfer_item(ctx.author.id, target.id, item_id, amount)
                response = create_response("transfer_item", 3, user=ctx.author.id, target=target.id, amount=amount)
                await ctx.respond("done")

            except VeyraError as e:
                await ctx.respond(str(e))


    @commands.command()
    async def checkinventory(self, ctx):
        """
        Prefix command to check your own inventory
        """
        status, embed = get_inventory(ctx.author.id, ctx.author.name)

        if status == "start_event":
            await ctx.send("hiiiiiii")  # todo: replace with starter event logic
        else:
            await ctx.send(embed=embed)



def setup(bot):
    bot.add_cog(Inventory(bot))