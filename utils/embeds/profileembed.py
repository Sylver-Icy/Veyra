import discord

from utils.emotes import GOLD_EMOJI

DIVIDER = "~" * 22


def _fmt_int(x, default=0):
    try:
        return int(x)
    except Exception:
        return default


def _fmt_dt(dt_value):
    if not dt_value:
        return "—"
    return str(dt_value)


def build_profile_embed_page_1(profile: dict) -> discord.Embed:
    identity = profile.get("identity", {})
    prog = profile.get("progression", {})
    inv = profile.get("inventory_summary", {})
    eco = profile.get("economy", {})
    battle = profile.get("battle", {}).get("loadout", {}) or {}

    user_name = identity.get("user_name", "Unknown")
    user_id = identity.get("user_id", "—")


    level = _fmt_int(prog.get("level"))
    exp = _fmt_int(prog.get("exp"))
    energy = _fmt_int(prog.get("energy"))
    stage = _fmt_int(prog.get("campaign_stage"))

    friendship = prog.get("friendship", {})
    friendship_title = friendship.get("title", "—")
    friendship_progress = friendship.get("progress", 0)

    total_items = _fmt_int(inv.get("total_items"))
    unique_items = _fmt_int(inv.get("unique_items"))

    gold = _fmt_int(eco.get("gold"))

    weapon = battle.get("weapon", "—")
    spell = battle.get("spell", "—")


    embed = discord.Embed(
        title=f"👤 Profile • {user_name}",
        description=f"**ID:** `{user_id}`",
    )

    embed.add_field(
        name="📈 Progression",
        value=(
            f"**Level:** `{level}`\n"
            f"**EXP:** `{exp}`\n"
            f"**Energy:** `{energy}` ⚡\n"
            f"**Campaign Stage:** `{stage}`"
        ),
        inline=False,
    )

    embed.add_field(name="\u200b", value=DIVIDER, inline=False)

    embed.add_field(
        name="🤝 Friendship",
        value=(
            f"**Title:** `{friendship_title}`\n"
            f"**Progress:** `{friendship_progress:.1f}%`"
        ),
        inline=True,
    )

    embed.add_field(
        name="💰 Economy",
        value=f"**Gold:** `{gold}` 🪙",
        inline=True,
    )

    embed.add_field(name="\u200b", value=DIVIDER, inline=False)

    embed.add_field(
        name="🎒 Inventory",
        value=(
            f"**Total Items:** `{total_items}`\n"
            f"**Unique Items:** `{unique_items}`"
        ),
        inline=False,
    )

    embed.add_field(name="\u200b", value=DIVIDER, inline=False)

    embed.add_field(
        name="⚔️ Battle Loadout",
        value=(
            f"**Weapon:** `{weapon}`\n"
            f"**Spell:** `{spell}`\n"
        ),
        inline=False,
    )


    embed.set_footer(text="Page 1/2 • Profile Overview")
    return embed


def build_profile_embed_page_2(profile: dict) -> discord.Embed:
    identity = profile.get("identity", {})
    stats = profile.get("stats", {}) or {}

    user_name = identity.get("user_name", "Unknown")

    battles_won = _fmt_int(stats.get("battles_won"))
    races_won = _fmt_int(stats.get("races_won"))
    quest_streak = _fmt_int(stats.get("longest_quest_streak"))
    weekly_rank1 = _fmt_int(stats.get("weekly_rank1_count"))
    biggest_lottery = _fmt_int(stats.get("biggest_lottery_win"))


    embed = discord.Embed(
        title=f"📊 Stats • {user_name}",
        description="Your lifetime performance stats.",
    )

    embed.add_field(
        name="🏆 **Battles Wins**",
        value=(
            f"Battles Won: `{battles_won}`\n"
            f"Races Won: `{races_won}`"
        ),
        inline=False,
    )

    embed.add_field(name="\u200b", value=DIVIDER, inline=False)

    embed.add_field(
        name="🔥 **Longest Quest Streaks**",
        value=f"`{quest_streak}`",
        inline=False,
    )

    embed.add_field(name="\u200b", value=DIVIDER, inline=False)

    embed.add_field(
        name="👑 **Times #1 on Weekly Leaderboard**",
        value=f"`{weekly_rank1}`",
        inline=False,
    )

    embed.add_field(name="\u200b", value=DIVIDER, inline=False)

    embed.add_field(
        name="🎰 **Lottery Biggest Win**",
        value=f"`{biggest_lottery}` {GOLD_EMOJI}",
        inline=False,
    )


    embed.set_footer(text="Page 2/2 • Player Stats")
    return embed


class ProfilePagerView(discord.ui.View):
    def __init__(self, profile: dict, author_id: int, timeout: float = 120):
        super().__init__(timeout=timeout)
        self.profile = profile
        self.author_id = author_id
        self.page = 1

    def _get_embed(self):
        if self.page == 1:
            return build_profile_embed_page_1(self.profile)
        return build_profile_embed_page_2(self.profile)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # only the command author can press buttons
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "Touch grass. This isn't your profile 😭", ephemeral=True
            )
            return False
        return True

    @discord.ui.button(label="⬅ Prev", style=discord.ButtonStyle.secondary)
    async def prev(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.page = 2 if self.page == 1 else 1
        await interaction.response.edit_message(embed=self._get_embed(), view=self)

    @discord.ui.button(label="Next ➡", style=discord.ButtonStyle.primary)
    async def next(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.page = 2 if self.page == 1 else 1
        await interaction.response.edit_message(embed=self._get_embed(), view=self)

    @discord.ui.button(label="🗑 Close", style=discord.ButtonStyle.danger)
    async def close(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.edit_message(content="Closed.", embed=None, view=None)
