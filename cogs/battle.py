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
from services.battle.battle_queue import try_to_start_battle_queue

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

    @commands.slash_command(description="Challenge another player to a PvP battle with a gold bet.")
    async def battle(self, ctx, target: discord.User, bet: int):
        """Challenge another player to a PvP battle.

        Flow:
        1) Validate target and bet amount.
        2) Ensure the challenger has enough gold.
        3) Deduct gold into the battle pot.
        4) Send a challenge prompt to the opponent.
        5) On accept → run battle simulation.
           On reject/timeout → refund the pot.
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



    @commands.slash_command(description="View and update your battle loadout (weapon & spell).")
    async def loadout(self, ctx):
        """Open the UI to view or change your equipped weapon and spell."""
        view, embed = get_loadout_ui(
            user=ctx.author,
            allowed_weapons=get_allowed_weapons(),
            allowed_spells=get_allowed_spells(),
        )

        await ctx.respond(embed=embed, view=view)

    @commands.slash_command(description="Fight Veyra in campaign mode (PvE progression).")
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
        """Start a PvE campaign battle.

        Battle against Veyra (or later NPCs) based on your campaign stage.
        Progress through stages to face stronger enemies and new loadouts.
        """

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

    @commands.slash_command(description="Enter the PvP queue and get matched automatically.")
    async def open_to_battle(
        self,
        ctx,
        min_bet: int = Option(
            int,
            description="Minimum bet you are willing to battle on",
            min_value = 10,
            max_value = 1000,
            required=True
        ),
        max_bet: int = Option(
            int,
            description="Max bet you are willing to battle one",
            min_value = 10,
            max_value = 10000,
            required=True
        )

    ):
        """Join the PvP matchmaking queue within a chosen bet range."""
        result = await try_to_start_battle_queue(ctx, ctx.author.id, min_bet, max_bet)
        if result and not ctx.response.is_done():
            await ctx.respond(result)



def setup(bot: commands.Bot):
    bot.add_cog(Battle(bot))