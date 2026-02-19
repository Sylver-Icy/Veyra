

import discord
from services.battle.loadout_services import update_loadout, fetch_loadout
from domain.battle.rules import get_weapon_label, get_spell_label


def build_loadout_embed(user, weapon, spell):
    embed = discord.Embed(
        title=f"{user.display_name}'s Loadout",
        color=discord.Color.blurple()
    )

    embed.add_field(
        name="⚔️ Equipped Weapon",
        value=f"**{weapon}**",
        inline=False
    )

    embed.add_field(
        name="✨ Equipped Spell",
        value=f"**{spell}**",
        inline=False
    )

    embed.set_footer(text="Use the dropdowns below to change your gear")
    return embed


class WeaponSelect(discord.ui.Select):
    def __init__(self, view):
        options = [
            discord.SelectOption(label=get_weapon_label(name), value=name)
            for name in view.allowed_weapons
        ]

        super().__init__(
            placeholder="Choose weapon",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        view = self.view

        if interaction.user.id != view.user_id:
            await interaction.response.send_message(
                "Not your loadout 😌",
                ephemeral=True
            )
            return

        result = update_loadout(view.user_id, weapon=self.values[0])

        if not result["success"]:
            await interaction.response.send_message(result["message"], ephemeral=True)
            return

        embed = build_loadout_embed(
            interaction.user,
            get_weapon_label(result["weapon"]),
            get_spell_label(result["spell"])
        )

        await interaction.response.edit_message(embed=embed, view=view)


class SpellSelect(discord.ui.Select):
    def __init__(self, view):
        options = [
            discord.SelectOption(label=get_spell_label(name), value=name)
            for name in view.allowed_spells
        ]

        super().__init__(
            placeholder="Choose spell",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        view = self.view

        if interaction.user.id != view.user_id:
            await interaction.response.send_message(
                "Not your loadout 😌",
                ephemeral=True
            )
            return

        result = update_loadout(view.user_id, spell=self.values[0])

        if not result["success"]:
            await interaction.response.send_message(result["message"], ephemeral=True)
            return

        embed = build_loadout_embed(
            interaction.user,
            get_weapon_label(result["weapon"]),
            get_spell_label(result["spell"])
        )

        await interaction.response.edit_message(embed=embed, view=view)


class LoadoutView(discord.ui.View):
    def __init__(self, user, allowed_weapons, allowed_spells):
        super().__init__(timeout=300)  # 5 minutes

        self.user_id = user.id
        self.allowed_weapons = allowed_weapons
        self.allowed_spells = allowed_spells

        weapon, spell = fetch_loadout(user.id)

        self.embed = build_loadout_embed(
            user,
            get_weapon_label(weapon),
            get_spell_label(spell)
        )

        self.add_item(WeaponSelect(self))
        self.add_item(SpellSelect(self))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "Hands off. Not yours.",
                ephemeral=True
            )
            return False
        return True

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True


# Convenience helper to build loadout embed + view.
def get_loadout_ui(user, allowed_weapons, allowed_spells):
    """
    Convenience helper to build loadout embed + view.

    Returns:
        view, embed
    """
    view = LoadoutView(user, allowed_weapons, allowed_spells)
    return view, view.embed