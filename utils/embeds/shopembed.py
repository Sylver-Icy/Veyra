import discord
from utils.emotes import GOLD_EMOJI
def shop_embed(shop_items: list) -> discord.Embed:
    """Creates a shop embed from a list of items"""
    embed = discord.Embed(
        title="Veyra's Bazaar",
        description="One of the best places to spend your gold! Return it all to Veyra!",
        color=discord.Color.green()
    )

    for item in shop_items:
        embed.add_field(
    name=f"**{item['name']}**\nID: {item['id']} | Price: {item['price']} {GOLD_EMOJI}",
    value=f"`{item['description']}`\nRarity: {item['rarity']}",
    inline=True
)
    embed.set_footer(text= "Shop refreshes every 24hrs")
    embed.set_image(url="https://cdn.discordapp.com/attachments/921681249817493554/1385331424252657765/images-3.jpeg?ex=6855aded&is=68545c6d&hm=bf6fb34e7ade73cf72400b2600aec1397330fcd8bc8b7d6bd168ac36a05da066&")
    return embed