import discord
from discord.ui import View, button

class LootboxView(View):
    def __init__(self, pages: list[discord.Embed]):
        super().__init__(timeout=160)
        self.pages = pages
        self.index = 0

    async def update_page(self, interaction: discord.Interaction):
        """Updates the embed and disables buttons on the last page."""
        # Disable buttons if we're on the last page
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = (self.index == len(self.pages) - 1)
        await interaction.response.edit_message(embed=self.pages[self.index], view=self)

    @button(label="Next →", style=discord.ButtonStyle.green)
    async def next_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.index < len(self.pages) - 1:
            self.index += 1
        await self.update_page(interaction)


def build_lootbox_embed_pages(rewards: dict) -> list[discord.Embed]:
    pages = []

    # --- Page 1: Gold Reward ---
    total_items = len(rewards.get("items", []))
    embed = discord.Embed(
        title="🎉 Lootbox Opened!",
        description=(
            f"You received **{rewards['gold']} gold**!\n\n"
            f"📦 You have **{total_items} item{'s' if total_items != 1 else ''}** to reveal..."
        ),
        color=discord.Color.gold()
    )
    embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/138/138292.png")
    embed.set_footer(text="Click Next → to reveal your loot!")
    pages.append(embed)

    # --- Item Pages ---
    for item in rewards.get("items", []):
        rarity_colors = {
            "common": discord.Color.light_grey(),
            "rare": discord.Color.blue(),
            "epic": discord.Color.purple(),
            "legendary": discord.Color.orange(),
        }
        embed = discord.Embed(
            title=f"🎁 {item['quantity']} × {item['item']}",
            description=item.get("description", "No description available."),
            color=rarity_colors.get(item['rarity'].lower(), discord.Color.greyple())
        )
        embed.add_field(
            name="Rarity",
            value=f"**{item['rarity'].capitalize()}**",
            inline=False
        )
        embed.set_footer(text="Click Next → to reveal more...")
        embed.set_thumbnail(url=item['icon'])
        pages.append(embed)

    # --- Final Summary Page ---
    summary = discord.Embed(
        title="📦 Lootbox Summary",
        description=f"You gained **{rewards['gold']} gold** and the following items:",
        color=discord.Color.brand_red()
    )
    if rewards.get("items"):
        for item in rewards["items"]:
            summary.add_field(
                name=f"{item['quantity']} × {item['item']}",
                value=f"{item['description']}\n Rarity: {item['rarity'].capitalize()}",
                inline=False
            )
    else:
        summary.add_field(name="No items found!", value="Better luck next time!", inline=False)

    pages.append(summary)

    return pages

def lootbox_embed_and_view(rewards: dict):
    pages = build_lootbox_embed_pages(rewards)
    view = LootboxView(pages)
    return(pages[0],view)