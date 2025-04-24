import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv("veyra.env")

TOKEN = os.getenv("DISCORD_TOKEN")
intent=discord.Intents.all()
bot=commands.Bot(command_prefix="!",intents=intent)

@bot.event
async def on_ready():
    """Send a conformation message when bot boots up"""
    print(f"logged in as {bot.user}")


cogs_list=[
    'games',
    'profile'
]

for cog in cogs_list:
    bot.load_extension(f'cogs.{cog}')

bot.run(TOKEN)
