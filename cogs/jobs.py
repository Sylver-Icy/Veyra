import discord
from discord.ext import commands
from services.jobs_services import JobsClass

class Jobs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="work", description="Perform a job to earn gold or items.")
    async def work(
        self,
        ctx: discord.ApplicationContext,
        job: discord.Option(str, "Choose a job to perform", choices=["knight", "digger", "miner", "thief", "explorer"]),
        target: discord.Option(discord.Member, "Who to steal from (thief only)", required=False, default=None),
    ):
        """Perform a job (knight, digger, miner, thief, explorer)."""
        worker = JobsClass(ctx.author.id)

        if job == "knight":
            result = worker.knight()
        elif job == "digger":
            result = worker.digger()
        elif job == "miner":
            result = worker.miner()
        elif job == "explorer":
            result = worker.explorer()
        elif job == "thief":
            if not target:
                await ctx.respond("You need to specify someone to steal from! You can't rob air can you?")
                return
            result = worker.thief(target)

        await ctx.respond(result)



def setup(bot):
    bot.add_cog(Jobs(bot))