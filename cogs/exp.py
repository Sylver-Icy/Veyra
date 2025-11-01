from discord.ext import commands
from discord.ext.commands import BucketType
from services.exp_services import current_exp
from services.response_services import create_response


class Exp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(1, 10, BucketType.user)
    async def checkexp(self, ctx):
        """Check your current EXP and level."""
        exp, level = current_exp(ctx.author.id)
        response = create_response(
            "check_exp",
            1,
            user=ctx.author.mention,
            level=level,
            exp=exp
        )
        await ctx.send(response)


def setup(bot):
    bot.add_cog(Exp(bot))