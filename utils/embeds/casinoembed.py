import discord
from discord.ui import View, button
from utils.emotes import GOLD_EMOJI, CHIP_EMOJI

# Optional flair emojis (safe fallback if your emotes module doesn’t have them)
SPARKLES = "✨"
TICKET = "🎟️"
ARROW = "➡️"
COIN = "🪙"


def casino_buy_embed(offers: dict) -> discord.Embed:
    """
    offers: dict keyed by id:
      {
        "401": {
          "name": "Copper Teaser",
          "gold_cost": 1000,
          "chips": 100,
          "bonus": 0,
        }
      }
    """
    embed = discord.Embed(
        title=f"{CHIP_EMOJI} **Buy Chips** {CHIP_EMOJI}",
        description=(
            "*Exchange gold for casino chips.*\n"
            "\n"
            "**How this works**\n"
            "• Buying chips unlocks casino games\n"
            "• Bigger packs usually give better value\n"
        ),
        color=discord.Color.gold(),
    )

    # Sort packs by price so the list feels intentional
    sorted_items = sorted(offers.items(), key=lambda kv: kv[1].get("gold_cost", 0))

    embed.add_field(name=f"{CHIP_EMOJI} Chip Packs", value="Pick a pack to exchange gold for chips.", inline=False)

    for pack_id, pack in sorted_items:
        bonus = int(pack.get("bonus", 0) or 0)
        base_chips = int(pack.get("chips", 0) or 0)

        gold_cost = int(pack.get("gold_cost", 0) or 0)

        bonus_text = f"+{bonus} bonus" if bonus > 0 else "No bonus"

        embed.add_field(
            name=f"**{pack.get('name', 'Unnamed Pack')}**",
            value=(
                f"{SPARKLES} **ID:** `{pack_id}`\n"
                f"{GOLD_EMOJI} **Price:** `{gold_cost}`\n"
                f"{CHIP_EMOJI} **Chips:** `{base_chips}` ({bonus_text})\n"
            ),
            inline=True,
        )

    embed.set_footer(text=f"{ARROW} Buy: !buychips <pack_id>   |   {ARROW} Convert: press the button below")
    embed.set_image(url="https://cdn.discordapp.com/attachments/921681249817493554/1463809646447038637/image.png")
    return embed


def casino_convert_embed(cashout_offers: dict) -> discord.Embed:
    """
    cashout_offers: dict keyed by pack_id (id is the key, NOT inside):
      {
        "501": {
          "name": "Loose Change Cashout",
          "chips_cost": 100,
          "gold_received": 500,
          "bonus_gold": 0,
        }
      }
    """
    embed = discord.Embed(
        title=f"{COIN} **Chip Cashout** {COIN}",
        description=(
            "*Convert chips back into gold.*\n"
            "\n"
            "**How this works**\n"
            "• Cashout packs give gold for chips\n"
            "• Bigger packs have higher bonus gold\n"
        ),
        color=discord.Color.gold(),
    )

    sorted_items = sorted(cashout_offers.items(), key=lambda kv: kv[1].get("chips_cost", 0))

    embed.add_field(name="🪙 Cashout Offers", value="Pick a pack to exchange chips for gold.", inline=False)

    for pack_id, pack in sorted_items:
        chips_cost = int(pack.get("chips_cost", 0) or 0)
        gold_received = int(pack.get("gold_received", 0) or 0)
        bonus_gold = int(pack.get("bonus_gold", 0) or 0)


        bonus_line = f"+{bonus_gold} bonus" if bonus_gold > 0 else "No bonus"

        embed.add_field(
            name=f"**{pack.get('name', 'Cashout')}**",
            value=(
                f"{SPARKLES} **ID:** `{pack_id}`\n"
                f"{CHIP_EMOJI} **Cost:** `{chips_cost}`\n"
                f"{GOLD_EMOJI} **Gold:** `{gold_received}` ({bonus_line})\n"
            ),
            inline=True,
        )

    embed.set_footer(text=f"{ARROW} Cashout: !cashout <pack_id>   |   {ARROW} Buy: press the button below")
    return embed


class CasinoView(View):
    def __init__(self, offers: dict, convert_data: dict):
        super().__init__(timeout=None)
        self.offers = offers
        self.convert_data = convert_data

    @button(label="Buy Chips", style=discord.ButtonStyle.green)
    async def buy_chips_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.edit_message(
            embed=casino_buy_embed(self.offers),
            view=self
        )

    @button(label="Convert Chips", style=discord.ButtonStyle.blurple)
    async def convert_chips_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.edit_message(
            embed=casino_convert_embed(self.convert_data),
            view=self
        )


def get_casino_view_and_embed(offers: dict, convert_data: dict):
    view = CasinoView(offers, convert_data)
    embed = casino_buy_embed(offers)
    return embed, view