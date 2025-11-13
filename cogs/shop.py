import logging
from discord.ext import commands
from utils.itemname_to_id import get_item_id_safe
from services.shop_services import buy_item, sell_item, daily_shop
from services.economy_services import add_gold

logger = logging.getLogger(__name__)
class Shop(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(1,5,commands.BucketType.user)
    async def buy(self, ctx, *args):
        """
        Buy Items from shop
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

        item_id,suggestions= get_item_id_safe(item_name) #gets the item id if name matches else suggests similiar names in case of typo
        if suggestions: #if suggestions has items it means not correct match was found
            await ctx.send(f"Item not found in database. I think you meant {suggestions[0]} ???")
            return
        response = buy_item(ctx.author.id, item_id, quantity)
        if response == "Purchase successful":
            await ctx.send(f"You bought {quantity} of {item_name.capitalize()}!!!")
            logger.info("%s bought %dX%s from bot", ctx.author.name, quantity, item_name)


        else:
            await ctx.send(response)

    @commands.command()
    @commands.cooldown(1,5,commands.BucketType.user)
    async def sell(self, ctx, *args):
        if len(args) < 2:
            await ctx.send("Usage: !sell [item name] [quantity]")
            return
        try:
            quantity = int(args[-1])
        except ValueError:
            await ctx.send("Quantity must be a number.")
            return
        item_name = " ".join(args[:-1]).lower()
        minerals = ("iron bar", "copper bar", "silver bar")
        if item_name.lower() in minerals:
            if item_name.lower() == "iron bar":
                price = 150
            elif item_name.lower() == "copper bar":
                price = 50
            else:
                price = 450

            revenue = price * quantity
            add_gold(ctx.author.id, revenue)
            await ctx.send(f"You sold {quantity} X {item_name.title()}!! Gold gained -> {revenue} ")
            return


        item_id,suggestions= get_item_id_safe(item_name) #gets the item id if name matches else suggests similiar names in case of typo
        if suggestions: #if suggestions has items it means not correct match was found
            await ctx.send(f"Item not found in database. You meant {suggestions[0]} ???")
            return
        response = sell_item(ctx.author.id, item_id, quantity)
        await ctx.send(response)

    @commands.slash_command()
    @commands.cooldown(1,15,commands.BucketType.user)
    async def shop(self,ctx):
       embed,view = daily_shop()
       await ctx.respond(embed=embed,view=view)

def setup(bot):
    bot.add_cog(Shop(bot))