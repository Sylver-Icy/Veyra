import discord
from discord.ext import commands

def create_quest_embed(quest: dict, progress: dict) -> discord.Embed:
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
    quest_reward = quest.get("reward", 0)

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

    # Add reward field
    embed.add_field(
        name="Reward",
        value=f"💰 {quest_reward}",
        inline=False
    )

    return embed