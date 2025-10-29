import discord
from discord.ui import View, button, Button

class BattleRequestView(View):
    def __init__(self, challenger: discord.User, target: discord.User, bet_amount: int):
        super().__init__(timeout=60)
        self.challenger = challenger
        self.target = target
        self.bet_amount = bet_amount
        self.accepted = None

    @button(label="Accept", style=discord.ButtonStyle.success)
    async def accept(self, button: Button, interaction: discord.Interaction):
        if interaction.user.id != self.target.id:
            await interaction.response.send_message("You can't accept someone else's challenge!", ephemeral=True)
            return

        self.accepted = True
        for child in self.children:
            child.disabled = True

        await interaction.response.edit_message(
            content=f"✅ {self.target.mention} accepted {self.challenger.mention}'s challenge!",
            view=self
        )
        self.stop()

    @button(label="Reject", style=discord.ButtonStyle.danger)
    async def reject(self, button: Button, interaction: discord.Interaction):
        if interaction.user.id != self.target.id:
            await interaction.response.send_message("You can't reject someone else's challenge!", ephemeral=True)
            return

        self.accepted = False
        for child in self.children:
            child.disabled = True

        await interaction.response.edit_message(
            content=f"❌ {self.target.mention} rejected {self.challenger.mention}'s challenge.",
            view=self
        )
        self.stop()


async def send_battle_challenge(ctx, challenger_id: int, target_id: int, bet_amount: int):
    """
    Sends a 1v1 battle request embed with accept/reject buttons using Pycord.
    """
    challenger = await ctx.bot.fetch_user(challenger_id)
    target = await ctx.bot.fetch_user(target_id)

    embed = discord.Embed(
        title="⚔️ 1v1 Battle Challenge",
        description=(
            f"{target.mention}, **{challenger.name}** has challenged you to a duel!\n\n"
            f"💰 **Bet:** {bet_amount}\n"
            f"🏆 **Winner Reward:** {bet_amount * 2}\n\n"
            f"Do you accept this challenge?"
        ),
        color=discord.Color.blurple()
    )
    embed.set_footer(text="You have 60 seconds to respond.")

    view = BattleRequestView(challenger, target, bet_amount)
    msg = await ctx.respond(embed=embed, view=view)
    await view.wait()

    if view.accepted is None:
        await msg.edit_original_response(content="⏰ Challenge timed out.", view=None)
        return None
    elif view.accepted:
        return True
    else:
        return False

    # services/discord_battle/battle_embed.py

MOVE_EMOJI = {
    "attack": "⚔️",
    "block": "🛡️",
    "counter": "🔁",
    "recover": "💧",
    "cast": "🔮",
}

def _stat_line(p) -> str:
    return f"HP **{max(p.hp, 0)}** | ATK **{max(p.attack, 0)}** | DEF **{max(p.defense, 0)}** | SPD **{max(p.speed, 0)}** | MANA **{max(p.mana, 0)}**"

def build_round_embed(round_num: int, p1, p2, challenger_name: str, target_name: str) -> discord.Embed:
    title = f"🎬 Round {round_num} — The Duel Begins"
    desc = (
        f"**{challenger_name}** and **{target_name}** step back into stance.\n"
        f"Choose your move within **50s** — or bleed **25 HP** to hesitation. ⏳\n\n"
        f"— — — — — — — — — — — —\n"
        f"**{challenger_name}** → {_stat_line(p1)}\n"
        f"**{target_name}** → {_stat_line(p2)}"
    )

    embed = discord.Embed(title=title, description=desc, color=discord.Color.blurple())
    embed.set_footer(text="Lock your move with the buttons below.")
    return embed

def _move_line(user_name: str, move: str | None, timed_out: bool) -> str:
    if timed_out:
        return f"⌛ **{user_name}** hesitated too long! **-25 HP** penalty."
    if move is None:
        return f"… **{user_name}** stands uncertain."
    emoji = MOVE_EMOJI.get(move, "❔")
    phrases = {
        "attack": f"{emoji} **{user_name}** lunges in with a vicious strike!",
        "block":  f"{emoji} **{user_name}** braces, shield up and eyes sharp.",
        "counter":f"{emoji} **{user_name}** baits the hit — ready to snap back!",
        "recover":f"{emoji} **{user_name}** steadies their breath, drawing in focus.",
        "cast":   f"{emoji} **{user_name}** weaves mana — a spell crackles to life!",
    }
    return phrases.get(move, f"{emoji} **{user_name}** acts…")

def build_result_embed(
    round_num: int,
    challenger_name: str, target_name: str,
    move_p1: str | None, move_p2: str | None,
    result_text: str,
    p1_timed_out: bool, p2_timed_out: bool,
) -> discord.Embed:
    title = f"🎬 Round {round_num} — Resolution"
    top = (
        f"{_move_line(challenger_name, move_p1, p1_timed_out)}\n"
        f"{_move_line(target_name, move_p2, p2_timed_out)}\n"
        "---------------------------- \n"
    )
    bot = f"\n💥 **Clash Report:** {result_text}\n"


    embed = discord.Embed(
        title=title,
        description=top + bot,
        color=discord.Color.purple()
    )
    embed.set_footer(text="New round starting...")
    return embed

def build_final_embed(winner_name: str | None, loser_name: str | None, bet: int, both_dead: bool = False) -> discord.Embed:
    if both_dead:
        title = "☠️ Double KO — No Survivors"
        desc = (
            "Both warriors fall in the same breath. The arena falls silent.\n\n"
            "💸 **Payout:** No winner — the pot vanishes to the void."
        )
        color = discord.Color.dark_gray()
    elif winner_name is None:
        title = "⚠️ Duel Concluded"
        desc = "The battle has ended unexpectedly."
        color = discord.Color.orange()
    else:
        title = "🏆 VICTORY!"
        desc = (
            f"**{winner_name}** triumphs in a glorious 1v1!\n"
            f"⚰️ **{loser_name}** falls where they stood.\n\n"
            f"💰 **Reward:** `{bet * 2}`"
        )
        color = discord.Color.gold()

    embed = discord.Embed(title=title, description=desc, color=color)
    embed.set_footer(text="GG. Train harder, come back sharper.")
    return embed