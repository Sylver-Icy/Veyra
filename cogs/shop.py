from discord.ext import commands
from services.shop_services import daily_shop,buy_item
from utils.itemname_to_id import item_name_to_id


class Shop(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    
    @commands.command()
    async def buy(self, ctx, *args):
        if len(args) < 2:
            await ctx.send("Usage: !buy [item name] [quantity]")
            return
        try:
            quantity = int(args[-1])
        except ValueError:
            await ctx.send("Quantity must be a number.")
            return
        item_name = " ".join(args[:-1]).lower()
        try:
            id = item_name_to_id[item_name]
        except KeyError:
            await ctx.send("Item not found in shop.")
            return
        a = buy_item(ctx.author.id, id, quantity)
        if a == "Purchase successful":
            await ctx.send(f"You bought {quantity} of {item_name.capitalize()}!!!")
        else:
            await ctx.send(a)

    @commands.slash_command()
    async def shop(self,ctx):
        embed = daily_shop()
        await ctx.respond (embed=embed)

def setup(bot):
    bot.add_cog(Shop(bot))