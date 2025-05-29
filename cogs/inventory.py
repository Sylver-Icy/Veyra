from discord.ext import commands
import discord
from discord import Option
import logging
from services.inventory_services import add_item as add_item_service, give_item as give_item_service
from utils.custom_errors import WrongItemError

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
            await ctx.respond("✅ Item successfully added.")
            logger.info("%s added %s to database", ctx.author.name, item_name)

    @commands.slash_command()
    async def give_item(self,ctx,target: discord.Member, item_id: int, amount: int):
        """Give items to users"""
        try:
            give_item_service(target.id, item_id, amount)
            await ctx.respond(f"{ctx.author} gave {amount} of item-{item_id} to {target}")
        except WrongItemError as e:
            await ctx.respond(e)
        
def setup(bot):
    bot.add_cog(Inventory(bot))