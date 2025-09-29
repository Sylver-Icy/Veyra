import discord
from discord.ui import View, button
from utils.emotes import GOLD_EMOJI


def shop_embed(shop_items: list) -> discord.Embed:
    """Creates a shop embed from a list of items"""
    embed = discord.Embed(
        title="**Veyra's Bazaar**",
        description="*One of the best places to spend your gold! Return it all to Veyra!*",
        color=discord.Color.green()
    )

    for item in shop_items:
        embed.add_field(
            name=f"**{item['name']}**\nID: {item['id']} | Price: {item['price']} {GOLD_EMOJI}",
            value=f"`{item['description']}`\nRarity: {item['rarity']}",
            inline=True
        )

    embed.set_author(name="Shop refreshes every 5 minutes")
    embed.set_footer(text="**How to buy** -> !buy <item_name> <amount>  e.g.  !buy sword 4")
    embed.set_image(url="https://cdn.discordapp.com/attachments/921681249817493554/1385331424252657765/images-3.jpeg")
    return embed


def buyback_shop_embed(shop_items: list) -> discord.Embed:
    """Create the second page embed for shop where it shows items bot is buying"""
    embed = discord.Embed(
        title="**Veyra's Bazaar**",
        description="*These are items I need you got them? I'll buy at a ***totally fair*** price <3 *",
        color=discord.Color.green()
    )
    for item in shop_items:
        embed.add_field(
            name=f"{item['name']} -> {item['price']} {GOLD_EMOJI}",
            value=item['description'],
            inline=False
        )
    embed.set_author(name="Shop refreshes every 5 minutes")
    embed.set_footer(text="How to sell -> !sell <item_name> <amount>  e.g.  !sell sword 4")
    return embed


class ShopView(View):
    def __init__(self, shop_items: list, buyback_items: list):
        super().__init__(timeout=None)
        self.shop_items = shop_items
        self.buyback_items = buyback_items

    @button(label="Shop", style=discord.ButtonStyle.green)
    async def shop_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.edit_message(
            embed=shop_embed(self.shop_items),
            view=self
        )

    @button(label="Buyback", style=discord.ButtonStyle.blurple)
    async def buyback_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.edit_message(
            embed=buyback_shop_embed(self.buyback_items),
            view=self
        )


def get_shop_view_and_embed(shop_items: list, buyback_items: list):
    """
    Returns a tuple (embed, view) so you can just call it in a cog.
    By default, the initial page will be the regular shop.
    """
    view = ShopView(shop_items, buyback_items)
    embed = shop_embed(shop_items)
    return embed, view