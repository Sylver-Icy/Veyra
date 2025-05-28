import discord
from discord.ext import commands
from discord.ext.commands import BucketType
from services.exp_services import current_exp
class Exp(commands.Cog):
    def __init__(self,bot):
        self.bot=bot

    @commands.command()
    @commands.cooldown(1,10,BucketType.user)
    async def checkexp(self,ctx):
         exp, level = current_exp(ctx.author.id)
         await ctx.send(f"Hello {ctx.author.name}! You're at level {level} with {exp} EXP points.")

def setup(bot):
    """Setup the Cog"""
    bot.add_cog(Exp(bot))