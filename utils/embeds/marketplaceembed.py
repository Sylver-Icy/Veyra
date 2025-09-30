import discord
from math import ceil

def build_marketplace(listings: list):
    # Split listings into pages of 9
    listings_per_page = 9
    pages = []

    total_pages = ceil(len(listings) / listings_per_page)

    if not listings:
        embed = discord.Embed(
            title="🛒 Marketplace",
            description="⚠️ No listings found.",
            color=discord.Color.blurple()
        )
        pages.append(embed)
        return pages

    for page_num in range(total_pages):
        start = page_num * listings_per_page
        end = start + listings_per_page
        current_listings = listings[start:end]

        embed = discord.Embed(
            title="🛒 Marketplace",
            description="Listings created by other users ↓",
            color=discord.Color.blurple()
        )

        for listing in current_listings:
            embed.add_field(
                name=f"📌 Listing #{listing['listing_id']}",
                value=(
                    f"🪶 **{listing['item_name']}**\n"
                    f"💰 Price: `{listing['price']}` per unit\n"
                    f"📦 Quantity: `{listing['quantity']}` available\n"
                    f"👤 Seller: `{listing['user_name']}`"
                ),
                inline=True
            )

        embed.set_footer(text=f"Page {page_num + 1} of {total_pages}")
        pages.append(embed)

    return pages
