import discord

def build_referral_card(
    username: str,
    total_invites: int,
    successful_invites: int,
    current_milestone: int | None,
    next_milestone: int | None,
    next_reward_name: str | None
):
    embed = discord.Embed(
        title=f"📨 {username}'s Referral Stats",
        color=discord.Color.gold()
    )

    embed.add_field(
        name="Total Invites",
        value=f"`{total_invites}`",
        inline=True
    )

    embed.add_field(
        name="Successful Invites (Reached Lv.5)",
        value=f"`{successful_invites}`",
        inline=True
    )

    embed.add_field(
        name="Current Reward Tier",
        value=f"`{current_milestone}`" if current_milestone else "`None`",
        inline=True
    )

    if next_milestone:
        embed.add_field(
            name="Next Reward At",
            value=f"`{next_milestone}` Invites",
            inline=True
        )

        embed.add_field(
            name="Next Reward",
            value=f"`{next_reward_name}`",
            inline=True
        )
    else:
        embed.add_field(
            name="Next Reward",
            value="`Max tier reached 👑`",
            inline=False
        )

    progress_bar = build_progress_bar(successful_invites, next_milestone)

    embed.add_field(
        name="Progress",
        value=progress_bar,
        inline=False
    )

    embed.set_footer(text="Rewards may take up to 24 hours after level-up to be credited. Thank you for helping support Veyra's development.")
    return embed


def build_progress_bar(current: int, target: int | None, length: int = 12):
    if not target:
        return "████████████ Maxed"

    ratio = min(current / target, 1)
    filled = int(ratio * length)
    empty = length - filled

    return f"{'█'*filled}{'░'*empty} {current}/{target}"