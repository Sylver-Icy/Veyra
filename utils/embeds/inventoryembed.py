import discord
def build_inventory(user_name: str,items: list):
    embed = discord.Embed(
        title = f"**{user_name}**'s inventory",
        description = "Here are all the items owned by you",
        color = discord.Colour.brand_red()
    )
    for item in items:
        embed.add_field(
            name=f"`{item['item_name']}` X {item['item_quantity']}",
            value=f"*{item['item_description']}* \nRarity: {item['item_rarity']}",
            inline=False
        )
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/921681249817493554/1385546878485266532/2897785.png?ex=68567696&is=68552516&hm=f88a7b1a913ba04fded51cc41024747011e3cce42acbd2d95e2b83c2b8a21ae4")
    return embed