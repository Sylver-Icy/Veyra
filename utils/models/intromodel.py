
import random
import discord
from discord.ui import Modal, InputText

# Intro channels per guild (duct-tape config)
INTRO_CHANNELS = {
    1419040189782818950: 1419055325931376811,  # Veyra main -> Veyra intro
    1334824535391997985: 1462405749362786324   # Lilith -> Lilith intro
}


def create_intro_modal(author: discord.Member):
    """Return a Pycord Modal for introduction."""


    class IntroModal(Modal):
        def __init__(self):
            super().__init__(title="🕯️ Forge Thy Identity")

            self.add_item(InputText(
                label="State thy Name and Title",
                placeholder="Example: Veyra, The Slayer",
                max_length=40
            ))

            self.add_item(InputText(
                label="Declare thy Class & Discipline",
                placeholder="Example: Hope of the Universe, Rune Alchemist, The Knave, Yellow Flash",
                max_length=40
            ))

            self.add_item(InputText(
                label="Reveal thy Main Questline",
                style=discord.InputTextStyle.long,
                placeholder="Example: Help build Veyra until she becomes self-aware",
                max_length=350
            ))

            self.add_item(InputText(
                label="List thy Strengths / Blessings",
                style=discord.InputTextStyle.long,
                placeholder="Example: Adaptive mind, late‑night strategist, luck wielding",
                max_length=300
            ))

            self.add_item(InputText(
                label="Confess thy Curse / Weakness",
                style=discord.InputTextStyle.long,
                placeholder="Example: Easily distracted, mortal energy, anime temptations",
                required=False,
                max_length=250
            ))

        @staticmethod
        def clean_text(txt: str):
            return txt.strip().capitalize()

        def determine_rarity(self, combined_text: str):
            # Base rarity distribution
            base_rates = {
                "Common 🪨": 0.50,
                "Uncommon 🩶": 0.25,
                "Rare 💎": 0.15,
                "Epic 🌑": 0.07,
                "Legendary ⚜️": 0.02,
                "Eldritch 🩸": 0.01
            }

            # Length-based mild scaling (max improvement when length >= 500)
            length = len(combined_text)
            effort_scale = min(length / 500, 1.0)

            # Mild rarity shift weights
            shift = {
                "Common 🪨": -0.20 * effort_scale,
                "Uncommon 🩶": -0.05 * effort_scale,
                "Rare 💎": 0.10 * effort_scale,
                "Epic 🌑": 0.09 * effort_scale,
                "Legendary ⚜️": 0.05 * effort_scale,
                "Eldritch 🩸": 0.01 * effort_scale
            }

            # Apply shifts
            adjusted = {r: base_rates[r] + shift[r] for r in base_rates}

            # Normalize to guarantee exact 100%
            total = sum(adjusted.values())
            normalized = {r: adjusted[r] / total for r in adjusted}

            # Roll gacha
            roll = random.random()
            cumulative = 0

            for rarity, rate in normalized.items():
                cumulative += rate
                if roll <= cumulative:
                    # Color mapping
                    colors = {
                        "Common 🪨": 0x565656,
                        "Uncommon 🩶": 0x7A7A7A,
                        "Rare 💎": 0x3A8FB7,
                        "Epic 🌑": 0x4B0082,
                        "Legendary ⚜️": 0xC9A227,
                        "Eldritch 🩸": 0x8B0000
                    }
                    return rarity, colors[rarity]

            # Fallback fail-safe
            return "Common 🪨", 0x565656

        async def callback(self, interaction: discord.Interaction):
            guild_id = interaction.guild.id
            INTRO_CHANNEL_ID = INTRO_CHANNELS.get(guild_id)
            if INTRO_CHANNEL_ID is None:
                return await interaction.response.send_message(
                    "⚠️ No intro channel configured for this realm.", ephemeral=True
                )

            channel = interaction.client.get_channel(INTRO_CHANNEL_ID)

            if channel is None:
                return await interaction.response.send_message(
                    "⚠️ Realm channel missing. The path is broken.", ephemeral=True
                )

            # Format answers
            title = self.clean_text(self.children[0].value)
            char_class = self.clean_text(self.children[1].value)
            quest = self.clean_text(self.children[2].value)
            blessings = self.clean_text(self.children[3].value)
            curse = self.clean_text(self.children[4].value) if self.children[4].value else "None spoken"

            # Determine rarity
            rarity, color = self.determine_rarity(
                f"{title}{char_class}{quest}{blessings}{curse}"
            )

            # Random opening lines
            headlines = [
                "🕯️ **A new tarnished crawls from the fog...**",
                "🌫️ **The mist swirls... a soul emerges.**",
                "🔥 **A wanderer approaches the ancient bonfire...**",
                "📜 **A forgotten rune‑bearer reveals their form.**",
                "🏹 **Another wanderer marks their fate in shadow.**",
                "⚔️ **The quiet realm trembles with new presence.**",
                "🔮 **Destiny drags forth yet another challenger.**",
                "🩸 **The pact of blood whispers… a new sigil forms.**",
                "⛓️ **Chains rattle — reality acknowledges another.**",
                "🖤 **The void watches with silent curiosity.**"
            ]
            intro_headline = random.choice(headlines)

            footer_lines = [
                "The runes remember only those who endure.",
                "Ashes or glory — the path accepts both.",
                "Some legends rise, others rot in silence.",
                "Even fate fears the will of the relentless.",
                "Only the lost learn the deepest truths.",
                "Glory is carved, not granted.",
                "The void sees potential... or delusion.",
                "Runes whisper of those who dare.",
                "A name means nothing without scars.",
                "Step forward, or be forgotten like the rest."
            ]
            random_footer = random.choice(footer_lines)

            embed = discord.Embed(
                title=f"{intro_headline}",
                color=color
            )

            embed.add_field(name="🏷️ Title", value=title, inline=False)
            embed.add_field(name="⚔️ Class", value=char_class, inline=False)
            embed.add_field(name="📜 Main Questline", value=quest, inline=False)
            embed.add_field(name="🧬 Strengths / Blessings", value=blessings, inline=False)
            embed.add_field(name="💀 Curse / Weakness", value=curse, inline=False)
            embed.add_field(name="🔮 Intro Tier", value=rarity, inline=False)

            embed.set_footer(text=random_footer)

            await channel.send(content=author.mention, embed=embed)
            await interaction.response.send_message(
                "Your introduction has been posted in #introductions", ephemeral=True
            )

    return IntroModal()