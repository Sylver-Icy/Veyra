import discord

async def send_dm(bot, user_id: int, embed: discord.Embed):
    """
    Send a DM embed to a user.

    Args:
        bot: Pycord bot instance
        user_id (int): Target user ID
        embed (discord.Embed): Embed to send

    Returns:
        bool: True if sent successfully, False otherwise
    """

    try:
        user = await bot.fetch_user(user_id)
        await user.send(embed=embed)
        return True

    except discord.Forbidden:
        return False

    except discord.HTTPException:
        return False
