import discord
from discord.ext import commands
from services.jobs_services import JobsClass

class Jobs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description="Perform a job (knight, digger, miner, thief, explorer).")
    async def work(
        self,
        ctx: discord.ApplicationContext,
        job: discord.Option(str, "Pick a job", choices=["knight", "digger", "miner", "thief", "explorer"]),
        target: discord.Option(discord.Member, "User to rob (required for thief)", required=False) = None,
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
