import discord
from discord.ext import commands
import logging
from utils.embeds.animalraceembed import race_cooldown_embed
# import utils.custom_errors as err
from utils.custom_errors import VeyraError

logger = logging.getLogger(__name__)

class ErrorHandler(commands.Cog):
    """Handles global command errors like cooldowns and permission issues."""
    def __init__(self, bot):
        self.bot = bot

    # Handle prefix command errors
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        original = getattr(error, "original", error)

        if isinstance(original, commands.CommandOnCooldown):
            retry_after = original.retry_after
            await ctx.send(f"🕒 Chill out! Try again in `{retry_after:.1f}` seconds.")
            logger.warning("%s hit cooldown on %s (retry in %.1fs)", ctx.author.name, ctx.command, original.retry_after)

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
            # Generic check failure (we don't know why). If a check raised VeyraError,
            # it would have been caught by the VeyraError branch.
            logger.warning("%s failed a custom check on %s", ctx.author.name, ctx.command)

        elif isinstance(original, commands.CommandNotFound):
            # Silently ignore unknown commands for prefix commands
            pass

        elif isinstance(original, VeyraError):
            await ctx.send(str(original))
            logger.warning("Veyra error from %s on %s: %s", ctx.author.name, ctx.command, str(error))

        else:
            await ctx.send("💥 An unexpected error occurred.")
            logger.exception("Unhandled error in prefix command: %s", error)

    # Handle slash command errors (Pycord uses on_slash_command_error)
    @commands.Cog.listener()
    async def on_application_command_error(self, ctx, error):
        original = getattr(error, "original", error)

        # NOTE:
        # Some global checks raise VeyraError (e.g., channel policy restrictions).
        # Those should be shown to the user. Only ignore generic check failures.
        if isinstance(original, VeyraError):
            await ctx.respond(str(original), ephemeral=True)
            logger.warning("Veyra policy/check error from %s on slash command %s: %s", ctx.author.name, ctx.command, str(error))
            return

        # Ignore generic global check failures completely (like DM-block)
        if isinstance(error, commands.CheckFailure) or isinstance(original, commands.CheckFailure):
            return

        if isinstance(original, commands.CommandOnCooldown):
            retry_after = original.retry_after
            if ctx.command and ctx.command.name == "start_race":
                embed,view = race_cooldown_embed(retry_after)
                await ctx.respond(embed=embed,view=view)
            else:
                await ctx.respond(f"🕒 You're on cooldown. Try again in `{retry_after:.1f}` seconds.", ephemeral=True)
            logger.warning("%s hit cooldown on slash command %s (retry in %.1fs)", ctx.author.name, ctx.command, original.retry_after)

        elif isinstance(original, commands.MissingPermissions):
            await ctx.respond("🚫 You don't have permission to do that.", ephemeral=True)
            logger.warning("%s tried to use slash command %s without permission.", ctx.author.name, ctx.command)

        elif isinstance(original, commands.MissingRequiredArgument):
            await ctx.respond("❗ You're missing an argument for this command.", ephemeral=True)
            logger.warning("%s used slash command %s missing required arguments.", ctx.author.name, ctx.command)

        elif isinstance(original, commands.BadArgument):
            await ctx.respond("❌ Invalid argument. Please check your input.", ephemeral=True)
            logger.warning("%s provided bad arguments for slash command %s.", ctx.author.name, ctx.command)

        elif isinstance(original, commands.BotMissingPermissions):
            await ctx.respond("⚠️ I don't have permission to do that.", ephemeral=True)
            logger.warning("Bot missing permissions for slash command %s in %s", ctx.command, ctx.guild.name)

        elif isinstance(original, commands.CommandNotFound):
            # Slash commands are always known, but just in case, ignore silently
            pass

        elif isinstance(original, VeyraError):
            await ctx.respond(str(original), ephemeral=True)
            logger.warning("Veyra error from %s on slash command %s: %s", ctx.author.name, ctx.command, str(error))

        elif isinstance(error, commands.CheckFailure):
            return

        else:
            await ctx.respond("💥 An unexpected error occurred.", ephemeral=True)
            logger.exception("Unhandled error in slash command: %s", error)

def setup(bot):
    """Setup the Cog"""
    bot.add_cog(ErrorHandler(bot))
