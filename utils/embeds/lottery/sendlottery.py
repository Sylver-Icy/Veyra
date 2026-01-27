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
        if old_msg:
            try:
                await old_msg.delete()
            except Exception as e:
                print(f"⚠️ Failed to delete old message in {guild_id}: {e}")

        embed, view = create_lottery_embed(ticket_price)
        msg = await channel.send(
            content="TIME TO TRY YOUR LUCK!!!!",
            embed=embed,
            view=view
        )

        last_lottery_messages[guild_id] = msg


async def send_result(bot):
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

        embed, winner_id = create_result_embed()
        await channel.send(
            content=f"Results are out!!!! \n <@{winner_id}> won today!",
            embed=embed
        )

    reset_lottery()