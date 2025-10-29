# services/discord_battle/battle_view.py
import discord
from discord.ui import View, button, Button

VALID_MOVES = ("attack", "block", "counter", "recover", "cast")

class BattleRoundView(View):
    """
    Collects moves from exactly two players by buttons.
    - Allows only the two specified user IDs.
    - Each user can lock exactly one move.
    - View stops automatically when both locked.
    """
    def __init__(self, p1_id: int, p2_id: int, timeout: float = 50.0):
        super().__init__(timeout=timeout)
        self.p1_id = p1_id
        self.p2_id = p2_id
        self.moves: dict[int, str] = {}  # {user_id: move}

    async def _handle_move(self, interaction: discord.Interaction, move: str):
        uid = interaction.user.id
        if uid not in (self.p1_id, self.p2_id):
            await interaction.response.send_message("Not your duel, chief.", ephemeral=True)
            return

        if uid in self.moves:
            await interaction.response.send_message("You already locked your move.", ephemeral=True)
            return

        self.moves[uid] = move
        await interaction.response.send_message(f"Locked **{move}** ✅", ephemeral=True)

        # Stop early once both decided
        if self.p1_id in self.moves and self.p2_id in self.moves:
            self.stop()

    @button(label="⚔️ Attack", style=discord.ButtonStyle.primary)
    async def btn_attack(self, button: Button, interaction: discord.Interaction):
        await self._handle_move(interaction, "attack")

    @button(label="🛡️ Block", style=discord.ButtonStyle.secondary)
    async def btn_block(self, button: Button, interaction: discord.Interaction):
        await self._handle_move(interaction, "block")

    @button(label="🔁 Counter", style=discord.ButtonStyle.secondary)
    async def btn_counter(self, button: Button, interaction: discord.Interaction):
        await self._handle_move(interaction, "counter")

    @button(label="💧 Recover", style=discord.ButtonStyle.success)
    async def btn_recover(self, button: Button, interaction: discord.Interaction):
        await self._handle_move(interaction, "recover")

    @button(label="🔮 Cast", style=discord.ButtonStyle.success)
    async def btn_cast(self, button: Button, interaction: discord.Interaction):
        await self._handle_move(interaction, "cast")

    async def on_timeout(self):
        # When timeout hits, just stop; the orchestrator decides penalties
        self.stop()