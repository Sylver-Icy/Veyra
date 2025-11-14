from discord.ext import commands

from services.crafting_services import smelt
from services.upgrade_services import building_lvl


class Crafting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command()
    async def smelt(self, ctx, bar_name: str, amount: int):
        if bar_name.lower() not in ("copper bar", "iron bar", "silver bar"):
            await ctx.respond("Ermm.. There is no such metal?")
            return

        smelter_lvl = building_lvl(ctx.author.id, "smelter")

        if  smelter_lvl == 0:
            await ctx.respond("You tryna smelt with your bare hands? Buy a furnace first, genius.\n`!unlock smelter`")
            return

        level = smelter_lvl
        allowed_bars = []
        coal_cost = 0

        if 1 <= level <= 2:
            allowed_bars = ["copper bar"] if level == 1 else ["copper bar", "iron bar"]
            coal_cost = 5 if level == 1 else 4
        elif 3 <= level <= 4:
            allowed_bars = ["copper bar", "iron bar"]
            coal_cost = 4 if level == 3 else 3
        elif 5 <= level <= 6:
            allowed_bars = ["copper bar", "iron bar", "silver bar"]
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