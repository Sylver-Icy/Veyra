import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from services.users_services import is_user
from responses import responses_loader
from utils.chatexp import chatexp
from utils.jobs import scheduler,run_at_startup
# from nsfw_classifier.nsfw_classifier import classify
from utils.logger import setup_logging
setup_logging()
load_dotenv("veyra.env")

TOKEN = os.getenv("DISCORD_TOKEN")
intent=discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intent, case_insensitive=True)

@bot.check
async def is_registered(ctx):
    """
    Global check to see if an user exits in database before allowing them commands
    """
    if ctx.command.name in ["helloVeyra","help"]: #Allow basic commands
        return True
    if not is_user(ctx.author.id): #If user is not registered ask them to register first
        await ctx.send("You are not frnds with Veyra! Use `!helloVeyra` to get started")
        return False

    return True #Allow command execution if registered

@bot.event
async def on_ready():
    """Start a scheduler and also send a conformation message when bot boots up"""
    run_at_startup()
    if not scheduler.running:
        scheduler.start()
    print(f"logged in as {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    # result,proba = classify(message.content)
    # if result == 1:
    #     await message.reply(f"Perv detected 🚨, {proba[1]:.2f}")
    # else:
    #     print(f"Sfw, {proba[0]:.2f}")
    #Logic to allow in line commands
    for command in bot.commands:
        if f"!{command.name}" in message.content:
            # Extract the command with everything after it
            command_start = message.content.index(f"!{command.name}")
            new_content = message.content[command_start:]

            # Create a new Message-like object with overridden content
            class ModifiedMessage(discord.Message):
                def __init__(self, original, new_content):
                    self._original = original
                    self._new_content = new_content

                @property
                def content(self):
                    return self._new_content

                def __getattr__(self, name):
                    return getattr(self._original, name)

            modified = ModifiedMessage(message, new_content)
            ctx = await bot.get_context(modified)
            await bot.invoke(ctx)
            return

    await bot.process_commands(message)

    #Give exp for chatting in servers
    if is_user(message.author.id):
        ctx = await bot.get_context(message)
        await chatexp(ctx)

cogs_list=[
    'games',
    'profile',
    'exp',
    'error_handler',
    'economy',
    'inventory',
    'shop',
    'lootbox'
]

for cog in cogs_list:
    bot.load_extension(f'cogs.{cog}')

bot.run(TOKEN)