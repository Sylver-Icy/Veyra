from discord.ext import commands

from services.crafting_services import smelt


class Crafting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command()
    async def smelt(self, ctx, bar_name: str, amount: int):
        result = smelt(ctx.author.id, bar_name, amount)

        await ctx.respond(result)


def setup(bot):
    bot.add_cog(Crafting(bot))