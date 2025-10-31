import asyncio
from discord.ext import commands

from services.users_services import is_user, add_user
from utils.embeds.help.helpembed import get_help_embed, get_command_info_embed

class Profile(commands.Cog):

    def __init__(self,bot):
        self.bot=bot

    @commands.command()
    async def helloVeyra(self, ctx):
        """
        Command for people to register themselves in the database.
        """
        user_id = ctx.author.id
        user_name = ctx.author.name

        if is_user(user_id): #Checks if the an already registered user is using the command
            await ctx.send(f"Hello {user_name}! nice to see you again :)")
        else:
            await ctx.send("Hy there wanna be frnds with me? (Yes/No)") #Initiates the registration process

            def check(m): #Checks if the message sent is sent by same user in same channel and is in correct form
                return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ["yes", "no"]

            try:
                msg = await self.bot.wait_for("message", timeout=30, check=check) #30 sec wait time for user to respond

                if msg.content.lower() == "yes":
                    await ctx.send("Yay! Welcome onboard 🎉")
                    add_user(user_id, user_name)
                else:
                    await ctx.send("Go fuck yourself 😇")

            except asyncio.TimeoutError: #If user didn't reply in 30 sec let them know command ended
                await ctx.send(f"Too slow ig you don't wanna be frnds {user_name}")

    @commands.slash_command()
    async def help(self,ctx):
        embed, view = get_help_embed(ctx.author)
        await ctx.respond(embed=embed, view=view)

    @commands.command()
    async def commandhelp(self, ctx, command_name):
        embed = get_command_info_embed(command_name)
        await ctx.send(embed=embed)


def setup(bot):
    """
    Set up the cog
    """
    bot.add_cog(Profile(bot))
