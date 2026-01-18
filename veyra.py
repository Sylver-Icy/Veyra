# veyra.py
"""
Main module for the Veyra Discord bot.

This module initializes the bot, sets up global checks, event handlers,
loads cogs, and starts the bot. It also manages background jobs and
handles inline command invocation and EXP system integration.
"""

import asyncio
import random

import os
import sys
import logging
from utils.logger import setup_logging
# SQLAlchemy model registration
import models  # Ensures all models are registered

import discord
from discord.ext import commands
from discord.ext.commands import Context
from discord import ApplicationContext

from dotenv import load_dotenv

# Setup early
load_dotenv("veyra.env")
setup_logging()
logger = logging.getLogger(__name__)

# Services
from services.users_services import is_user
from services.talk_to_veyra.chat_services import handle_user_message, fetch_channel_msgs
from services.onboadingservices import greet
from services.friendship_services import check_friendship
from services.response_services import create_response
from services.tutorial_services import tutorial_guard

from utils.jobs import scheduler, run_at_startup
from utils.chatexp import chatexp
from utils.jobs import schedule_jobs
from utils.fuzzy import get_closest_command
from utils.custom_errors import WrongChannelError, ServerRestrictedError


from domain.guild.guild_config import get_config, is_channel_allowed, ChannelPolicy

# from nsfw_classifier.nsfw_classifier import classify  # Optional feature

# Bot setup
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    logger.critical("DISCORD_TOKEN is not set or empty. Exiting.")
    sys.exit(1)

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, case_insensitive=True, help_command=None)



# ─── GLOBAL CHECKS ────────────────────────────────────────────────

@bot.check
async def block_dms(ctx):
    if ctx.guild is None:
        if hasattr(ctx, "respond"):
            await ctx.respond("DMs disabled.", ephemeral=True)
        else:
            await ctx.send("DMs disabled.")
        return False
    return True

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

@bot.check
async def channel_policy_guard(ctx):
    # no command = ignore
    if ctx.command is None or ctx.guild is None:
        return True

    cfg = get_config(ctx.guild.id)

    # get policy label from command callback function
    callback = getattr(ctx.command, "callback", None) or ctx.command
    policy_label = getattr(callback, "__channel_policy__", "spam")

    #convert to ChannelPolicy
    policy = ChannelPolicy.ANY if policy_label == "non_spam" else ChannelPolicy.SPAM_ONLY

    #validate channel
    if is_channel_allowed(cfg, ctx.channel.id, policy):
        return True

    #raise pretty error
    allowed_ids = cfg.allowed_spam_channel_ids if policy == ChannelPolicy.SPAM_ONLY else (cfg.allowed_non_spam_channel_ids or set()) | (cfg.allowed_spam_channel_ids or set())
    if allowed_ids:
        chans = " ".join(f"<#{cid}>" for cid in allowed_ids)
        raise WrongChannelError(f"❌ Use this command in: {chans}")

    raise WrongChannelError("❌ This command isn’t allowed in this channel.")


@bot.check
async def tutorial_check(ctx):
    if ctx.command is None or ctx.command.name in ["helloVeyra", "help"]:
        return True

    # 🚨 normalize args for prefix vs slash
    if isinstance(ctx, Context):
        # prefix commands: [self, ctx, *user_args]
        content = ctx.message.content
        parts = content.split()
        args = parts[1:]  # everything after command
    elif isinstance(ctx, ApplicationContext):
        # slash commands: options dict -> values
        args = list(ctx.options.values()) if ctx.options else []
    else:
        args = []

    blocked = await tutorial_guard(
        ctx,
        ctx.command.name,
        args
    )

    if blocked:
        raise commands.CheckFailure("Blocked by tutorial")

    return True


# ─── EVENTS ───────────────────────────────────────────────────────

@bot.event
async def on_ready():
    """Run background jobs and log when the bot is ready."""
    try:
        await run_at_startup(bot)
        schedule_jobs(bot)
        if not scheduler.running:
            scheduler.start()
        logger.info(f"✅ Veyra is online as {bot.user}")
    except Exception as e:
        logger.error(f"Error during on_ready: {e}", exc_info=True)

@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name='welcum')
    if channel:
        embed = greet(member.display_name)
        await channel.send(content=member.mention, embed=embed)

@bot.event
async def on_message(message):
    """Handle custom message logic (inline commands, EXP system, etc.)."""
    if message.author.bot:
        return

    msg_lower = message.content.lower()
    # Fuzzy command correction
    if msg_lower.startswith("!"):
        raw_cmd = msg_lower[1:].split(" ")[0]  # text after !
        closest = get_closest_command(raw_cmd)

        if closest and closest != raw_cmd:
            fixed_message = f"!{closest}" + message.content[len(raw_cmd)+1:]

            class ModifiedMessage(discord.Message):
                def __init__(self, original, new_content):
                    self._original = original
                    self._new_content = new_content

                @property
                def content(self):
                    return self._new_content

                def __getattr__(self, attr):
                    return getattr(self._original, attr)

            modified = ModifiedMessage(message, fixed_message)
            ctx = await bot.get_context(modified)
            if random.random() < 0.24:
                response = create_response("typo", 1, typo = raw_cmd, correct = closest)
                await ctx.send(response)

            await bot.invoke(ctx)
            return
    if message.channel.id == 1437565988966109318 and (bot.user in message.mentions or "veyra" in msg_lower) and msg_lower != "!helloveyra":
        async with message.channel.typing():
            await asyncio.sleep(random.uniform(0.5, 2))
            title, _ = check_friendship(message.author.id)
            msg_history = await fetch_channel_msgs(message.channel, bot_id=bot.user.id)

            # Generate reply
            reply = await handle_user_message(
                message.content,
                title,
                message.author.id,
                message.author.display_name,
                msg_history
            )

        await message.reply(reply)


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
    'battle',
    "crafting",
    "jobs",
    "upgrades"
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
