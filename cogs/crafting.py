"""crafting.py

Slash commands related to crafting.

Currently includes:
- /smelt: Smelt ores into metal bars (requires a smelter building).

This cog should stay as a thin command layer: validate input, then delegate work
to the services layer.
"""

from discord.ext import commands

from services.crafting_services import smelt
from services.upgrade_services import building_lvl


class Crafting(commands.Cog):
    """Crafting-related slash commands."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(description="Smelt ores into metal bars using your smelter.")
    async def smelt(self, ctx, bar_name: str, amount: int):
        """Smelt a metal bar.

        The user can pass shorthand names like `copper` and we normalize them.
        Smelting availability + coal cost depends on the user's smelter level.
        """

        # Normalize common aliases so users don't have to type exact item names.
        aliases = {
            "copper": "copper bar",
            "iron": "iron bar",
            "silver": "silver bar",
            "copper bar": "copper bar",
            "iron bar": "iron bar",
            "silver bar": "silver bar",
        }

        raw = bar_name.lower().strip()
        bar_name = aliases.get(raw)

        # Unknown / invalid metal.
        if bar_name is None:
            return await ctx.respond("Ermm.. There is no such metal?")

        # Determine user smelter level.
        smelter_lvl = building_lvl(ctx.author.id, "smelter")

        level = smelter_lvl
        allowed_bars = []
        coal_cost = 0

        # Smelter progression:
        # - Higher level unlocks more bars and reduces coal cost.
        if 1 <= level <= 2:
            allowed_bars = ["copper bar"] if level == 1 else ["copper bar", "iron bar"]
            coal_cost = 5 if level == 1 else 4
        elif 3 <= level <= 4:
            allowed_bars = ["copper bar", "iron bar"]
            coal_cost = 4 if level == 3 else 3
        elif 5 <= level <= 6:
            allowed_bars = ["copper bar", "iron bar", "silver bar"]
            coal_cost = 3 if level == 5 else 2
        elif level == 7:
            allowed_bars = ["copper bar", "iron bar", "silver bar"]
            coal_cost = 1

        # Disallow smelting bars that the current smelter level hasn't unlocked.
        if bar_name not in allowed_bars:
            return await ctx.respond("Your smelter can’t handle that metal yet!")

        # Delegate actual smelting logic to services.
        result = smelt(ctx.author.id, bar_name, amount, coal_cost)
        await ctx.respond(result)


def setup(bot: commands.Bot):
    """Discord.py extension entrypoint."""
    bot.add_cog(Crafting(bot))