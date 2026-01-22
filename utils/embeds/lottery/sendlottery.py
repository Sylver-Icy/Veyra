
from utils.embeds.lottery.lotteryembed import create_lottery_embed, create_result_embed
from services.lottery_services import reset_lottery

last_lottery_message = None  # store the latest message object globally


async def send_lottery(bot, ticket_price: int, channel_id=1275870091002777643, guild_id=1275870089228320768):
    global last_lottery_message  # to modify the global variable

    guild = bot.get_guild(guild_id)
    if not guild:
        print(f"Guild {guild_id} not found.")
        return

    channel = guild.get_channel(channel_id)
    if not channel:
        print(f"Channel {channel_id} not found.")
        return

    # delete old message if it exists
    if last_lottery_message:
        try:
            await last_lottery_message.delete()
        except Exception as e:
            print(f"⚠️ Failed to delete old message: {e}")

    # create and send new lottery embed
    embed, view = create_lottery_embed(ticket_price)
    last_lottery_message = await channel.send(content="TIME TO TRY YOUR LUCK!!!!", embed=embed, view=view)



async def send_result(bot, channel_id=1436044897340887191, guild_id=1419040189782818950):

    guild = bot.get_guild(guild_id)
    if not guild:
        print(f"Guild {guild_id} not found.")
        return

    channel = guild.get_channel(channel_id)
    if not channel:
        print(f"Channel {channel_id} not found.")
        return

    embed, winner_id = create_result_embed()
    await channel.send(content=f"Results are out!!!! \n <@{winner_id}> won today!", embed=embed)

    reset_lottery()