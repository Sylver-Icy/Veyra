import time

from discord.ext import commands
from discord.ext.commands import BucketType

from services.exp_services import current_exp
from services.response_services import create_response
from services.friendship_services import add_friendship

user_cooldowns = {}

class Exp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        """Give EXP every time a command successfully runs."""
        if ctx.author.bot:
            return

        now = time.time()
        user_id = ctx.author.id

        # Prevent EXP farming
        if user_id in user_cooldowns and now - user_cooldowns[user_id] < 10:
            return  # 10s cooldown per user for EXP gain

        user_cooldowns[user_id] = now
        add_friendship(user_id, 1)

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