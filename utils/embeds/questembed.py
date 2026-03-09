import discord
from discord.ext import commands
from utils.emotes import GOLD_EMOJI

def create_quest_embed(quest: dict, progress: dict, expires_at=None) -> discord.Embed:
    """
    Creates a quest embed with a visual progress bar.

    Args:
        quest: Dictionary containing quest information (name, description, reward, etc.)
        progress: Dictionary containing progress data (current, total, percentage)

    Returns:
        discord.Embed: Formatted embed with quest details and progress bar
    """

    # Extract quest and progress data
    quest_name = quest.get("name", "Unknown Quest")
    quest_description = quest.get("description", "No description")
    rewards = quest.get("reward", [])

    current_progress = progress.get("current", 0)
    total_progress = progress.get("total", 100)
    percentage = (current_progress / total_progress * 100) if total_progress > 0 else 0

    # Create progress bar
    bar_length = 20
    filled = int(bar_length * percentage / 100)
    progress_bar = "█" * filled + "░" * (bar_length - filled)

    # Create embed
    embed = discord.Embed(
        title=f"📜 {quest_name}",
        description=quest_description,
        color=discord.Color.gold()
    )

    # Add progress field
    embed.add_field(
        name="Progress",
        value=f"`{progress_bar}`\n{current_progress}/{total_progress} ({percentage:.1f}%)",
        inline=False
    )

    # Build reward display from list
    reward_lines = []
    for r in rewards:
        rtype = r.get("type")
        amount = r.get("amount", 0)
        if rtype == "gold":
            reward_lines.append(f"{amount} {GOLD_EMOJI}")
        elif rtype == "xp":
            reward_lines.append(f"✨ {amount} XP")
        elif rtype == "item":
            item_name = r.get("item_name", "Item")
            reward_lines.append(f"📦 {amount}x {item_name}")

    embed.add_field(
        name="Reward",
        value="\n".join(reward_lines) if reward_lines else "💰 0",
        inline=False
    )

    if expires_at is not None:
        ts = int(expires_at.timestamp())
        embed.add_field(
            name="Time Remaining",
            value=f"\u23f0 Expires <t:{ts}:R>",
            inline=False
        )

    return embed


def create_quest_complete_embed(quest: dict, rewards_granted: list) -> discord.Embed:
    """
    Creates an embed for a completed quest showing claimed rewards.
    """
    quest_name = quest.get("name", "Unknown Quest")

    embed = discord.Embed(
        title=f"\U0001f389 Quest Complete: {quest_name}",
        description="You completed your quest! Here's what you earned:",
        color=discord.Color.green()
    )

    reward_lines = []
    for r in rewards_granted:
        rtype = r.get("type")
        amount = r.get("amount", 0)
        if rtype == "gold":
            reward_lines.append(f"{amount} {GOLD_EMOJI}")
        elif rtype == "xp":
            reward_lines.append(f"\u2728 {amount} XP")
        elif rtype == "item":
            item_name = r.get("item_name", "Item")
            reward_lines.append(f"\U0001f4e6 {amount}x {item_name}")

    embed.add_field(
        name="Rewards",
        value="\n".join(reward_lines) if reward_lines else "No rewards",
        inline=False
    )

    embed.set_footer(text="Run /quest to get a new quest!")
    return embed