import discord
from discord.ext import commands
import logging
# import utils.custom_errors as err
from utils.custom_errors import VeyraError

logger = logging.getLogger(__name__)

class ErrorHandler(commands.Cog):
    """Handles global command errors like cooldowns and permission issues."""
    def __init__(self,bot):
        self.bot=bot
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        original = getattr(error, "original", error)
        if isinstance(original, commands.CommandOnCooldown):
            retry_after = original.retry_after
            await ctx.send(f"🕒 Chill out! Try again in `{retry_after:.1f}` seconds.")
            logger.warning("%s hit cooldown on %s (retry in %.1fs)", ctx.author.name, ctx.command, retry_after)

        elif isinstance(original, commands.MissingPermissions):
            await ctx.send("🚫 You don't have permission to do that.")
            logger.warning("%s tried to use %s without permission.", ctx.author.name, ctx.command)

        elif isinstance(original, commands.MissingRequiredArgument):
            await ctx.send("❗ You're missing an argument for this command.")
            logger.warning("%s used %s missing required arguments.", ctx.author.name, ctx.command)

        elif isinstance(original, commands.BadArgument):
            await ctx.send("❌ Invalid argument. Please check your input.")
            logger.warning("%s provided bad arguments for %s.", ctx.author.name, ctx.command)

        elif isinstance(original, commands.BotMissingPermissions):
            await ctx.send("⚠️ I don't have permission to do that.")
            logger.warning("Bot missing permissions for %s in %s", ctx.command, ctx.guild.name)
        elif isinstance(original, commands.CheckFailure):
            logger.warning( "%s failed a custom check on %s", ctx.author.name,ctx.command)

        elif isinstance(original, commands.CommandNotFound):
            pass 
        elif isinstance(original, VeyraError):
            await ctx.send(original)
            logger.warning("Veyra error from %s on %s: %s", ctx.author.name, ctx.command, str(error))
        else:
            await ctx.send("💥 An unexpected error occurred.")
            logger.exception("Unhandled error in command: %s", error)

def setup(bot):
    """Setup the Cog"""
    bot.add_cog(ErrorHandler(bot))