from discord.ext import commands

from services.crafting_services import smelt
from services.upgrade_services import building_lvl


class Crafting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command()
    async def smelt(self, ctx, bar_name: str, amount: int):
        smelter_lvl = building_lvl(ctx.author.id, "smelter")

        if  smelter_lvl == 0:
            await ctx.respond("You don't have a smelter yet! Buy one first.\n`!unlock smelter`")
            return

        level = smelter_lvl
        allowed_bars = []
        coal_cost = 0

        if 1 <= level <= 2:
            allowed_bars = ["copper bar"]
            coal_cost = 5
        elif 3 <= level <= 4:
            allowed_bars.append("iron bar")
            coal_cost = 4 if level == 3 else 3
        elif 5 <= level <= 6:
            allowed_bars.append("silver bar")
            coal_cost = 3 if level == 5 else 2
        elif level == 7:
            allowed_bars = ["copper bar", "iron bar", "silver bar"]
            coal_cost = 1

        if bar_name.lower() not in allowed_bars:
            await ctx.respond("Your smelter can’t handle that metal yet!")
            return

        result = smelt(ctx.author.id, bar_name, amount, coal_cost)
        await ctx.respond(result)


def setup(bot):
    bot.add_cog(Crafting(bot))