import discord
from math import ceil
import random

footers = (
    "Hmmm why don't you sell some of these on marketplace?",
    "Try /quest maybe you can make money off your items",
    "You know I can buy these? /shop then checkbuy to know what I need today",
    "What are you checking? Planning to trade these with others or sell them back to me?"
)

def build_inventory(user_name: str,items: list):
    pages=[] #empty list to store pages
    if not items:
        embed = discord.Embed(
            title = f"**{user_name}**'s inventory",
            description= "LOL its empty like your friend list",
            color=discord.Colour.nitro_pink()
        )
        pages.append(embed)

    else:
        items_per_page = 9
        total_pages = ceil(len(items)/items_per_page)

        for page_num in range(total_pages):
            start = page_num*items_per_page
            end = start + items_per_page
            current_items = items[start:end]
            embed = discord.Embed(
                title = f"**{user_name}**'s inventory",
                description = "Here are all the items owned by you",
                color = discord.Colour.brand_red()
            )
            for item in current_items:
                embed.add_field(
                    name=f"`{item['item_name']}` X {item['item_quantity']}       `{item['item_rarity']}` ",
                    value=f"*{item['item_description']}* \n  ------------------------------------------------------",
                    inline=False
                )
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/921681249817493554/1385546878485266532/2897785.png?ex=68567696&is=68552516&hm=f88a7b1a913ba04fded51cc41024747011e3cce42acbd2d95e2b83c2b8a21ae4")
            random_footer = random.choice(footers)
            embed.set_footer(text=random_footer)
            pages.append(embed)

    return pages

def build_item_info_embed(item: dict):
    rarity_colors = {
            "common": discord.Color.light_grey(),
            "rare": discord.Color.blue(),
            "epic": discord.Color.purple(),
            "legendary": discord.Color.orange(),
        }
    embed = discord.Embed(
        title= item['name'],
        description= item['description'],
        color= rarity_colors.get(item['rarity'])
    )
    embed.add_field(
        name="Rarity",
        value=item['rarity']
    )
    icon_url = item.get('icon')
    if icon_url and icon_url.startswith("http"):
        embed.set_thumbnail(url=icon_url)
    else:
        embed.set_thumbnail(url="https://cdn.discordapp.com/embed/avatars/0.png")  # fallback
    return embed