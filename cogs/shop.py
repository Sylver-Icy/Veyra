from discord.ext import commands
from services.shop_services import daily_shop,buy_item
from utils.itemname_to_id import item_name_to_id


class Shop(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    
    @commands.command()
    async def buy(self, ctx, item_name: str, quantity: int = 1):
        id = item_name_to_id[item_name]
        buy_item(ctx.author.id,id,quantity)
        await ctx.send(f"You want to buy {quantity} of {item_name}.")

    @commands.slash_command()
    async def shop(self,ctx):
        embed = daily_shop()
        await ctx.respond (embed=embed)

def setup(bot):
    bot.add_cog(Shop(bot))