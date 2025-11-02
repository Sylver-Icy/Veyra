import logging
from discord.ext import commands, pages
from services.inventory_services import give_item, take_item
from services.lootbox_services import lootbox_reward, user_lootbox_count, open_box
from services.economy_services import add_gold
from utils.itemname_to_id import item_name_to_id

logger = logging.getLogger(__name__)

class Lootbox(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(1,5,commands.BucketType.user)
    async def open(self, ctx, *, lootbox_name: str):
        """Open a lootbox and receive a random reward."""
        if lootbox_name.lower() not in ("wooden box", "stone box", "iron box", "platinum box"):
            await ctx.send(
                "❌ Incorrect box name. Available boxes are:\n"
                "• Wooden Box\n"
                "• Stone Box\n"
                "• Iron Box\n"
                "• Platinum Box\n"
                "Choose wisely :)"
            )
            return

        lootbox_amount = user_lootbox_count(ctx.author.id, lootbox_name)

        # Invalid lootbox
        if lootbox_amount == -1:
            await ctx.send(
                "❌ Incorrect box name. Available boxes are:\n"
                "• Wooden Box\n"
                "• Stone Box\n"
                "• Iron Box\n"
                "• Platinum Box\n"
                "Choose wisely :)"
            )
            return

        # No lootboxes of this type
        if lootbox_amount == 0:
            await ctx.send(f"You don’t have any **{lootbox_name.title()}**. What are you tryna open, huh?")
            return

        # Consume one lootbox
        item_id = lootbox_amount #the func returns item_id when box exists

        take_item(ctx.author.id, item_id, 1)

        # Get reward
        embed,view = open_box(ctx.author.id, lootbox_name)
        await ctx.send(embed=embed, view=view)

def setup(bot):
    bot.add_cog(Lootbox(bot))