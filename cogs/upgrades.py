import asyncio
from discord.ext import commands

from services.upgrade_services import buy_building, get_next_upgrade_info, upgrade_building


class Upgrades(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def unlock(self, ctx, building_name):
        response = buy_building(ctx.author.id, building_name)
        await ctx.send (response)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def upgrade(self, ctx, building_name):
        next_upgrade = get_next_upgrade_info(ctx.author.id, building_name)
        if isinstance(next_upgrade, str):
            await ctx.send(next_upgrade)
            return

        description = next_upgrade.get('description', 'No description available.')
        cost = next_upgrade.get('cost', 'Unknown cost')
        current_lvl = next_upgrade.get('current_level', '0')
        await ctx.send(f"The next upgrade effects are: {description}\nCost: {cost}\nAre you sure you want to upgrade your {building_name.title()} to level {current_lvl+1}? Type `yes` to confirm.")

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            msg = await self.bot.wait_for('message', timeout=15.0, check=check)
            if msg.content.lower() == 'yes':
                response = upgrade_building(ctx.author.id, building_name)
                await ctx.send(response)
            else:
                await ctx.send("Upgrade cancelled.")
        except asyncio.TimeoutError:
            await ctx.send("Upgrade cancelled.")


def setup(bot):
    bot.add_cog(Upgrades(bot))