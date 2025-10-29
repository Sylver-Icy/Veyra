# veyra.py
import os
from utils.logger import setup_logging
# SQLAlchemy model registration
import models  # Ensures all models are registered
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Setup early
load_dotenv("veyra.env")
setup_logging()

# Services
from services.users_services import is_user
from utils.jobs import scheduler, run_at_startup
from utils.chatexp import chatexp
# from nsfw_classifier.nsfw_classifier import classify  # Optional feature

# Bot setup
TOKEN = os.getenv("DISCORD_TOKEN")
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
    run_at_startup()
    if not scheduler.running:
        scheduler.start()
    print(f"✅ Veyra is online as {bot.user}")


@bot.event
async def on_message(message):
    """Handle custom message logic (inline commands, EXP system, etc.)"""
    if message.author.bot:
        return

    # --- Optional NSFW check ---
    # result, proba = classify(message.content)
    # if result == 1:
    #     await message.reply(f"Perv detected 🚨, {proba[1]:.2f}")
    # else:
    #     print(f"SFW, {proba[0]:.2f}")

    # Inline command support
    for command in bot.commands:
        if f"!{command.name}" in message.content:
            command_start = message.content.index(f"!{command.name}")
            new_content = message.content[command_start:]

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

    await bot.process_commands(message)

    # Give EXP for chatting
    if is_user(message.author.id):
        ctx = await bot.get_context(message)
        await chatexp(ctx)


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
    bot.load_extension(f'cogs.{cog}')


# ─── START BOT ────────────────────────────────────────────────────

bot.run(TOKEN)
