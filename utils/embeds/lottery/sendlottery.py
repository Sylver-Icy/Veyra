from utils.embeds.lottery.lotteryembed import create_lottery_embed, create_result_embed
from services.lottery_services import reset_lottery

# Temporary duct-tape multi-guild lottery targets
LOTTERY_TARGETS = [
    {
        "guild_id": 1419040189782818950,   # Veyra main
        "channel_id": 1436044897340887191
    },
    {
        "guild_id": 1334824535391997985,   # Lilith
        "channel_id": 1465704663281045750
    }
]

# store latest message per guild
last_lottery_messages = {}
last_result_messages = {}


async def _delete_previous_posts(channel, bot_user_id: int, content_prefix: str, cached_message=None):
    if cached_message:
        try:
            await cached_message.delete()
        except Exception as e:
            print(f"⚠️ Failed to delete cached lottery message in {channel.guild.id}: {e}")

    async for msg in channel.history(limit=15):
        if msg.author.id != bot_user_id:
            continue
        if not (msg.content or "").startswith(content_prefix):
            continue
        try:
            await msg.delete()
        except Exception as e:
            print(f"⚠️ Failed to delete prior lottery message in {channel.guild.id}: {e}")

async def send_lottery(bot, ticket_price: int):
    for target in LOTTERY_TARGETS:
        guild_id = target["guild_id"]
        channel_id = target["channel_id"]

        guild = bot.get_guild(guild_id)
        if not guild:
            print(f"Guild {guild_id} not found.")
            continue

        channel = guild.get_channel(channel_id)
        if not channel:
            print(f"Channel {channel_id} not found.")
            continue

        # delete old message if it exists
        old_msg = last_lottery_messages.get(guild_id)
        await _delete_previous_posts(
            channel,
            bot.user.id,
            "TIME TO TRY YOUR LUCK!!!!",
            cached_message=old_msg,
        )

        embed, view = create_lottery_embed(ticket_price)
        msg = await channel.send(
            content="TIME TO TRY YOUR LUCK!!!!",
            embed=embed,
            view=view
        )

        last_lottery_messages[guild_id] = msg


async def send_result(bot):
    # pick winner ONCE globally
    embed, winner_id = create_result_embed()

    for target in LOTTERY_TARGETS:
        guild_id = target["guild_id"]
        channel_id = target["channel_id"]

        guild = bot.get_guild(guild_id)
        if not guild:
            print(f"Guild {guild_id} not found.")
            continue

        channel = guild.get_channel(channel_id)
        if not channel:
            print(f"Channel {channel_id} not found.")
            continue

        # delete old result message if it exists
        old_msg = last_result_messages.get(guild_id)
        await _delete_previous_posts(
            channel,
            bot.user.id,
            "Results are out!!!!",
            cached_message=old_msg,
        )

        content = "Results are out!!!!"
        if winner_id is None:
            content += "\nNo one bought tickets today."
        else:
            content += f"\n <@{winner_id}> won today!"

        msg = await channel.send(content=content, embed=embed)

        last_result_messages[guild_id] = msg

    reset_lottery()
