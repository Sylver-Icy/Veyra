# veyra.py
"""
Main module for the Veyra Discord bot.

This module initializes the bot, sets up global checks, event handlers,
loads cogs, and starts the bot. It also manages background jobs and
handles inline command invocation and EXP system integration.
"""

import os
import sys
import logging
from utils.logger import setup_logging
# SQLAlchemy model registration
import models  # Ensures all models are registered
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Setup early
load_dotenv("veyra.env")
setup_logging()
logger = logging.getLogger(__name__)

# Services
from services.users_services import is_user
from utils.jobs import scheduler, run_at_startup
from utils.chatexp import chatexp
# from nsfw_classifier.nsfw_classifier import classify  # Optional feature

# Bot setup
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    logger.critical("DISCORD_TOKEN is not set or empty. Exiting.")
    sys.exit(1)

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, case_insensitive=True)


# ─── GLOBAL CHECKS ────────────────────────────────────────────────

@bot.check
async def is_registered(ctx):
    """
    Global check to ensure a user is registered before using most commands.
    Allows basic commands like helloVeyra/help unconditionally.
    """
    if ctx.command.name in ["helloVeyra", "help"]:
        return True

    if not is_user(ctx.author.id):
        await ctx.send("You are not frnds with Veyra! Use `!helloVeyra` to get started.")
        return False

    return True


# ─── EVENTS ───────────────────────────────────────────────────────

@bot.event
async def on_ready():
    """Run background jobs and log when the bot is ready."""
    try:
        run_at_startup()
        if not scheduler.running:
            scheduler.start()
        logger.info(f"✅ Veyra is online as {bot.user}")
    except Exception as e:
        logger.error(f"Error during on_ready: {e}", exc_info=True)


@bot.event
async def on_message(message):
    """Handle custom message logic (inline commands, EXP system, etc.)."""
    if message.author.bot:
        return

    msg_lower = message.content.lower()

    # Inline command support: check if message contains a command invocation inline
    for command in bot.commands:
        if f"!{command.name.lower()}" in msg_lower:
            try:
                command_start = msg_lower.index(f"!{command.name.lower()}")
                new_content = message.content[command_start:]

                # Create a modified message object that overrides content with the command substring
                class ModifiedMessage(discord.Message):
                    def __init__(self, original, new_content):
                        self._original = original
                        self._new_content = new_content

                    @property
                    def content(self):
                        return self._new_content

                    def __getattr__(self, attr):
                        return getattr(self._original, attr)

                modified = ModifiedMessage(message, new_content)
                ctx = await bot.get_context(modified)
                await bot.invoke(ctx)
                return
            except Exception as e:
                logger.error(f"Error invoking inline command '{command.name}': {e}", exc_info=True)
                # Do not swallow the message, continue processing

    await bot.process_commands(message)

    # Give EXP for chatting
    if is_user(message.author.id):
        try:
            ctx = await bot.get_context(message)
            await chatexp(ctx)
        except Exception as e:
            logger.error(f"Error processing chatexp for user {message.author.id}: {e}", exc_info=True)


# ─── LOAD COGS ────────────────────────────────────────────────────

cogs_list = [
    'games',
    'profile',
    'exp',
    'error_handler',
    'economy',
    'inventory',
    'shop',
    'lootbox',
    'marketplace',
    'gambling',
    'battle'
]

for cog in cogs_list:
    try:
        bot.load_extension(f'cogs.{cog}')
        logger.info(f"Loaded cog: {cog}")
    except Exception as e:
        logger.error(f"Failed to load cog {cog}: {e}", exc_info=True)


# ─── START BOT ────────────────────────────────────────────────────

try:
    bot.run(TOKEN)
except Exception as e:
    logger.critical(f"Bot failed to start: {e}", exc_info=True)
    sys.exit(1)
