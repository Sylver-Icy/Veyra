import discord

from services.economy_services import get_richest_users
from services.users_services import inc_top_leaderboard

from utils.emotes import GOLD_EMOJI

async def gold_leaderboard_embed(bot):

    embed = discord.Embed(
        title="🏆 Richest Players",
        description="The elite few who made the gold rain 💰",
        color=discord.Color.gold()
    )
    rich_users = get_richest_users()
    for i, wallet in enumerate(rich_users, start=1):
        user = await bot.fetch_user(wallet.user_id)
        embed.add_field(
            name=f"#{i} — {user.name}",
            value=f"{GOLD_EMOJI} {wallet.gold:,}",
            inline=False
        )

    embed.set_footer(text="Veyra’s economy leaderboard — updated live!")

    return embed

async def weekly_gold_leaderboard(bot):
    embed = discord.Embed(
        title="👑 Weekly Gold Overlords",
        description="Each coin, a story. Each name, a legend. Here stand the three who ruled Veyra’s economy this week.",
        color=discord.Color.gold()
    )

    medals = {
        1: ("🥇", "The unstoppable tycoon of wealth."),
        2: ("🥈", "The silver strategist who played the market like a game."),
        3: ("🥉", "The bronze grinder who clawed their way to glory.")
    }

    rich_users = get_richest_users(3)
    for i, wallet in enumerate(rich_users, start=1):
        user = await bot.fetch_user(wallet.user_id)
        medal, tagline = medals.get(i, ("💰", "A true gold hoarder."))

        if i == 1:
            inc_top_leaderboard(wallet.user_id)

        embed.add_field(
            name=f"{medal} #{i} — {user.name}",
            value=f"{GOLD_EMOJI} {wallet.gold:,}\n*{tagline}*",
            inline=False
        )
        if i < 3:
            embed.add_field(name="\u200b", value="─" * 20, inline=False)


    embed.set_footer(text="Veyra’s economy leaderboard — updated live!")

    return embed