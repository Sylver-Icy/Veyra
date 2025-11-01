import discord
from utils.embeds.leaderboard.leaderboardembed import weekly_gold_leaderboard

async def send_weekly_leaderboard(bot, guild_id = 1352515074886996062, channel_id = 1434228570380566559):
    """
    Sends the weekly leaderboard embed to a specific channel.

    Args:
        bot: The active bot instance.
        guild_id (int): The ID of the guild (server).
        channel_id (int): The ID of the text channel to send to.
    """
    guild = bot.get_guild(guild_id)
    if not guild:
        print(f"Guild {guild_id} not found.")
        return

    channel = guild.get_channel(channel_id)
    if not channel:
        print(f"Channel {channel_id} not found.")
        return

    embed = await weekly_gold_leaderboard(bot)
    await channel.send(content="@everyone 👑 Weekly Leaderboard Drop!", embed=embed)