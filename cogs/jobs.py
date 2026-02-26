import discord
from discord.ext import commands
from services.jobs_services import JobsClass

class Jobs(commands.Cog):
    work = discord.SlashCommandGroup("work", "Perform a job")

    def __init__(self, bot):
        self.bot = bot

    @work.command(name="knight", description="Work as a knight")
    async def work_knight(self, ctx: discord.ApplicationContext):
        worker = JobsClass(ctx.author.id)
        result = worker.knight()
        await ctx.respond(result)

    @work.command(name="digger", description="Work as a digger")
    async def work_digger(self, ctx: discord.ApplicationContext):
        worker = JobsClass(ctx.author.id)
        result = worker.digger()
        await ctx.respond(result)

    @work.command(name="miner", description="Work as a miner")
    async def work_miner(self, ctx: discord.ApplicationContext):
        worker = JobsClass(ctx.author.id)
        result = worker.miner()
        await ctx.respond(result)

    @work.command(name="explorer", description="Work as an explorer")
    async def work_explorer(self, ctx: discord.ApplicationContext):
        worker = JobsClass(ctx.author.id)
        result = worker.explorer()
        await ctx.respond(result)

    @work.command(name="thief", description="Steal from someone")
    async def work_thief(self, ctx: discord.ApplicationContext, target: discord.Member):
        worker = JobsClass(ctx.author.id)
        result = worker.thief(target)
        await ctx.respond(result)



def setup(bot):
    bot.add_cog(Jobs(bot))