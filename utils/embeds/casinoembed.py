import discord
from discord.ui import View, button
from utils.emotes import GOLD_EMOJI, CHIP_EMOJI


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
        title="**Veyra's Casino**",
        description="*Welcome to the casino. Please gamble responsibly (lol).*",
        color=discord.Color.gold()
    )

    for pack_id, pack in offers.items():
        bonus = int(pack.get("bonus", 0) or 0)
        total_chips = pack["chips"] + bonus
        bonus_text = f" (+{bonus} bonus)" if bonus > 0 else ""
        embed.add_field(
            name=f"**{pack['name']}**\nID: {pack_id} | Price: {pack['gold_cost']} {GOLD_EMOJI}",
            value=f"You get: **{total_chips}** {CHIP_EMOJI}{bonus_text}",
            inline=True
        )

    embed.set_author(name="Casino deals refresh daily")
    embed.set_footer(text="**How to buy** -> !buychips <pack_id>  e.g.  !buychips pack1")
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
        title="**Veyra's Casino**",
        description="*Convert chips → gold. Casino still wins. Always.*",
        color=discord.Color.gold()
    )

    for pack_id, pack in cashout_offers.items():
        bonus_gold = int(pack.get("bonus_gold", 0) or 0)
        total_gold = pack["gold_received"] + bonus_gold
        bonus_text = f" (+{bonus_gold} bonus)" if bonus_gold > 0 else ""

        embed.add_field(
            name=(
                f"**{pack['name']}**\n"
                f"ID: {pack_id} | Cost: {pack['chips_cost']} {CHIP_EMOJI}"
            ),
            value=f"You receive: **{total_gold}** {GOLD_EMOJI}{bonus_text}",
            inline=True
        )

    embed.set_author(name="Cashout deals refresh daily")
    embed.set_footer(text="**How to cashout** -> !cashout <pack_id>  e.g.  !cashout 501")
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