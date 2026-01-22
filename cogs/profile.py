import asyncio
from discord.ext import commands

from services.users_services import is_user, add_user, get_user_profile_new
from services.inventory_services import give_item
from services.friendship_services import check_friendship
from services.response_services import create_response
from services.jobs_services import JobsClass


from utils.models.intromodel import create_intro_modal
from utils.embeds.help.helpembed import get_help_embed, get_command_info_embed, get_json_pages_embed
from utils.embeds.profileembed import ProfilePagerView, build_profile_embed_page_1

from domain.guild.commands_policies import non_spam_command

class Profile(commands.Cog):

    def __init__(self,bot):
        self.bot=bot
        self.users_pending = set()

    @commands.command()
    @commands.cooldown(1,15,commands.BucketType.user)
    @non_spam_command()
    async def helloVeyra(self, ctx):
        """
        Command for people to register themselves in the database.
        """
        user_id = ctx.author.id
        user_name = ctx.author.name

        if is_user(user_id): #Checks if  an already registered user is using the command
            title, progress = check_friendship(user_id)
            if title in ("Stranger", "Acquaintance", "Casual"):
                response = create_response("friendship_check", 1, user=user_name, title=title, progress=progress)

            elif title in ("Friend", "Close Friend"):
                response = create_response("friendship_check", 2, user=user_name, title=title, progress=progress)

            else:
                response = create_response("friendship_check", 3, user=user_name, title=title, progress=progress)

            await ctx.send(response)
        else:
            if user_id in self.users_pending:
                await ctx.send("You haven't replied to me my previous message. YOU WANNA BE FRIEND WITH ME OR NOT.")
                return
            self.users_pending.add(user_id)
            await ctx.send("Hy there wanna be frnds with me? (Yes/No)") #Initiates the registration process

            def check(m): #Checks if the message sent is sent by same user in same channel and is in correct form
                return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ["yes", "no"]

            try:
                msg = await self.bot.wait_for("message", timeout=30, check=check) #30 sec wait time for user to respond

                if msg.content.lower() == "yes":
                    await ctx.send("Yay! Here keep these bags of gold as a gift for our new friendship ^^\n OH!! and also why don't you use `/introduction` and introduce yourself to everyone")
                    add_user(user_id, user_name)
                    give_item(user_id, 183, 2, True)
                    self.users_pending.remove(user_id)
                    user = JobsClass(user_id)
                    user.gain_energy(150) #give 150 energy on registration

                else:
                    self.users_pending.remove(user_id)
                    await ctx.send("Go fuck yourself 😇")

            except asyncio.TimeoutError: #If user didn't reply in 30 sec let them know command ended
                self.users_pending.remove(user_id)
                await ctx.send(f"Too slow ig you don't wanna be frnds {user_name}")

    @commands.slash_command()
    @commands.cooldown(1,25,commands.BucketType.user)
    @non_spam_command()
    async def help(self,ctx):
        embed, view = get_help_embed(ctx.author)
        await ctx.respond(embed=embed, view=view)

    @commands.command()
    @commands.cooldown(1,5,commands.BucketType.user)
    @non_spam_command()
    async def commandhelp(self, ctx, *, command_name):
        embed = get_command_info_embed(command_name)
        await ctx.send(embed=embed)


    @commands.command()
    async def details(self, ctx, topic):
        embed, view = get_json_pages_embed(ctx.author, topic.lower())
        msg = await ctx.send(embed=embed, view=view)
        if view:
            view.message = msg


    @commands.slash_command()
    @non_spam_command()
    async def introduction(self, ctx):
        modal = create_intro_modal(ctx.author)
        await ctx.send_modal(modal)


    @commands.slash_command()
    @commands.cooldown(1,250,commands.BucketType.user)
    @non_spam_command()
    async def profile(self,ctx):
        profile = get_user_profile_new(ctx.author.id)

        view = ProfilePagerView(profile=profile, author_id=ctx.author.id)
        await ctx.respond(embed=build_profile_embed_page_1(profile), view=view)




def setup(bot):
    """
    Set up the cog
    """
    bot.add_cog(Profile(bot))
