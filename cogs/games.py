import discord
from discord.ext import commands

class Games(commands.Cog):

    def __init__(self,bot):
        self.bot=bot
    
    @commands.command()
    async def ping(self,ctx):
        """The legendary Ping-Pong game"""
        await ctx.send("🏓Pong!")

def setup(bot):
    """Setup the Cog"""
    bot.add_cog(Games(bot))