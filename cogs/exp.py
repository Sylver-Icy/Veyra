import discord
from discord.ext import commands
from discord.ext.commands import BucketType
from services.exp_services import current_exp
from services.response_services import create_response
class Exp(commands.Cog):
    def __init__(self,bot):
        self.bot=bot

    @commands.command()
    @commands.cooldown(1,10,BucketType.user)
    async def checkexp(self,ctx):
         exp, level = current_exp(ctx.author.id)
         response =  create_response("check_exp", 1, user = ctx.author.mention, level=level, exp=exp) #creating response for the bot to send when user uses !checkexp
         await ctx.send(response)

def setup(bot):
    """Setup the Cog"""
    bot.add_cog(Exp(bot))