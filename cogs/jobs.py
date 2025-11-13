import discord
from discord.ext import commands
from services.jobs_services import JobsClass

class Jobs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def work(self, ctx, job: str, target: discord.Member = None):
        """Perform a job (knight, digger, miner, thief)."""
        valid_jobs = ("knight", "digger", "miner", "thief")

        if job not in valid_jobs:
            await ctx.send(f"Available jobs: {', '.join(valid_jobs)}")
            return

        worker = JobsClass(ctx.author.id)

        if job == "knight":
            result = worker.knight()
        elif job == "digger":
            result = worker.digger()
        elif job == "miner":
            result = worker.miner()
        elif job == "thief":
            if not target:
                await ctx.send("You need to specify someone to steal from! You can't rob air can you?")
                return
            result = worker.thief(target)

        await ctx.send(result)

    @commands.command()
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def checkenergy(self, ctx):
        worker = JobsClass(ctx.author.id)
        energy =  worker.check_energy()
        await ctx.send(f"You current have {energy} energy...")


def setup(bot):
    bot.add_cog(Jobs(bot))