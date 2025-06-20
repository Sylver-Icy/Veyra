from discord.ext import commands
import discord
from discord import Option
import logging
from services.inventory_services import add_item as add_item_service, give_item as give_item_service
from services.users_services import is_user
from utils.custom_errors import WrongItemError
from utils.itemname_to_id import item_name_to_id,suggest_similar_item

logger = logging.getLogger(__name__)

class Inventory(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    
    @commands.slash_command()
    async def add_item(self,
                    ctx,
                    item_id: int,
                    item_name: str,
                    item_description: str,
                    item_rarity: str = Option(
                        str,
                        choices=["Common", "Rare", "Epic", "Legendary", "Paragon"],
                        description="Select the rarity of item"
                    ),
                    item_icon: str = None,
                    item_durability: int = None):
        """Adds an item to database"""

        if add_item_service(item_id, item_name, item_description, item_rarity, item_icon, item_durability):
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
        item_id = item_name_to_id.get(item_name.capitalize())
        #Suggest items to  user if they made a typo
        if not item_id:
            suggestions = suggest_similar_item(item_name)
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
    
    

def setup(bot):
    bot.add_cog(Inventory(bot))