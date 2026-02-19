"""battle.py

Slash commands for PvP battles and the campaign battle mode.

This cog is intentionally thin: it validates user input and delegates the actual
battle logic to the services layer.

NOTE: Per project convention, keep this file focused on command handling only.
"""

import discord
from discord.ext import commands
from discord import Option

from utils.embeds.battleembed import send_battle_challenge

from services.battle.battle_simulation import (
    start_battle_simulation,
    start_campaign_battle,
)
from services.economy_services import check_wallet, remove_gold, add_gold
from services.users_services import is_user
from services.battle.loadout_services import update_loadout
from services.battle.campaign.campaign_services import (
    fetch_veyra_loadout,
    get_campaign_stage,
)
from services.battle.campaign.campaign_config import CAMPAIGN_LEVELS

from utils.embeds.loadoutembed import get_loadout_ui

from domain.battle.rules import get_allowed_weapons, get_allowed_spells

class Battle(commands.Cog):
    """Battle-related commands.

    Commands:
    - /battle: Challenge another user to a 1v1 battle with a bet.
    - /loadout: Update weapon/spell loadout used in battles.
    - /campaign: Fight Veyra in campaign mode (PvE).
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(description="Challenge someone to a 1v1 battle.")
    async def battle(self, ctx, target: discord.User, bet: int):
        """Challenge a user to a battle.

        Workflow:
        1) Validate target and bet.
        2) Ensure challenger can afford the bet.
        3) Deduct bet (pot money).
        4) Send challenge UI; on accept, run simulation; otherwise refund.
        """

        # --- Target sanity checks ---
        if target.id == ctx.author.id:
            await ctx.respond("Loner ultra pro max plus.", ephemeral=True)
            return

        if target.id == self.bot.user.id:
            await ctx.respond("You ain't gonna win so lets save ourselves some hassle.")
            return

        if not is_user(target.id):
            await ctx.respond(
                f"I can't initiate a battle with {target.display_name} they're not frnds with me."
            )
            return

        # --- Bet validation ---
        if bet <= 0:
            await ctx.respond("Bruh don't gamble if you can't afford", ephemeral=True)
            return

        # Prevent starting a battle the user can't pay for.
        if bet > check_wallet(ctx.author.id):
            await ctx.respond(
                "You don't have enough gold to initiate the challege. Try betting lower.",
                ephemeral=True,
            )
            return

        # Take gold as pot money (refunded if rejected/timeout).
        remove_gold(ctx.author.id, bet)

        # Send interactive challenge prompt.
        result = await send_battle_challenge(ctx, ctx.author.id, target.id, bet)

        if result is True:
            await ctx.send(f"🔥 {ctx.author.mention} vs {target.mention} — the battle begins!")
            await start_battle_simulation(ctx, ctx.author, target, bet)

        elif result is False:
            # Rejected: refund pot.
            add_gold(ctx.author.id, bet)
            await ctx.send(
                f"{ctx.author.mention}, your challenge was rejected. You pot money was refunded."
            )

        else:
            # Timed out / no response: refund pot.
            await ctx.send("No response. Challenge expired. Refunding pot gimme a moment.")
            add_gold(ctx.author.id, bet)



    @commands.slash_command()
    async def loadout(self, ctx):
        """Update your loadout (weapon + spell)."""
        view, embed = get_loadout_ui(
            user=ctx.author,
            allowed_weapons=get_allowed_weapons(),
            allowed_spells=get_allowed_spells(),
        )

        await ctx.respond(embed=embed, view=view)

    @commands.slash_command(description="Fight me in campaign mode.")
    async def campaign(
        self,
        ctx,
        delay: int = Option(
            int,
            description="Seconds between rounds (3-30). Leave empty for default.",
            min_value=3,
            max_value=30,
            required=False
        )
    ):
        """Start a campaign (PvE) fight against Veyra."""

        stage = get_campaign_stage(ctx.author.id)

        npc_name = "Veyra" if stage <= 10 else "Bardok"

        level_data = CAMPAIGN_LEVELS.get(stage, {})
        weapon_name = level_data.get("weapon", "Unknown")
        spell_name = level_data.get("spell", "Unknown")
        lore = level_data.get("lore", "")

        # Stage 11 is treated as campaign completion.
        if stage == 16:
            await ctx.respond(
                "You have already completed the campaign. Well done, warrior!\n"
                "Here some tea for ya 🍵 while you wait for new levels"
            )
            return

        await ctx.respond(
            "⚔️ Campaign battle starting...\n"
            f"Stage {stage}\n"
            f"{npc_name}'s Weapon: {weapon_name}\n"
            f"{npc_name}'s Spell: {spell_name}\n"
            + (f"\n📜 {lore}" if lore else "")
        )

        await start_campaign_battle(ctx, ctx.author, delay)


def setup(bot: commands.Bot):
    bot.add_cog(Battle(bot))