import discord
from discord.ext import commands

import os, json

_HELP_JSON_CACHE = {}

def load_json(path: str):
    if path not in _HELP_JSON_CACHE:
        with open(path, "r", encoding="utf-8") as f:
            _HELP_JSON_CACHE[path] = json.load(f)
    return _HELP_JSON_CACHE[path]

class HelpView(discord.ui.View):
    def __init__(self, user: discord.User):
        super().__init__(timeout=300)  # 5 min timeout
        self.user = user
        self.current_page = "prefix"

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user.id:
            await interaction.response.send_message(
                "❌ Only the person who used this command can use these buttons.", ephemeral=True
            )
            return False
        return True

    async def update_embed(self, interaction: discord.Interaction):
        if self.current_page == "prefix":
            embed = discord.Embed(
                title="📜 Prefix Commands",
                description="Use these commands with `!` before the command name.\n\n**Example:** `!balance`, `!shop`",
                color=discord.Color.blurple()
            )
            embed.add_field(name="🔥 Stats", value="`!check` - View your different stats", inline=False)
            embed.add_field(name="😶‍🌫️ Gambling", value="`!bet` - Place your bets during active races.", inline=False)
            embed.add_field(name="🎲 Fun", value="`!ping` - The legendary ping-pong game.\n"
                                                 "`!solve_wordle` - Let me solve your Wordle if the hints aren’t enough, cutie"
                                                 "\n`!play` - We can play a number guessing game :3" \
                                                 "\n`!flipcoin` - Let gacha decide your fate", inline=False)
            embed.add_field(name="🗃️ Inventory", value="`!info` - Confused? I can tell you about any item — just name it!"
            "\n`!use` - Use any usable item from your inventory.", inline=False)
            embed.add_field(name="😵‍💫 Lootbox", value="`!open` - Got boxes? I can open them for you :3", inline=False)
            embed.add_field(name="🛒 Shop", value="`!buy` - Purchase anything available in today’s shop.\n"
                                                  "`!sell` - Sell your items if they’re in the buyback section.", inline=False)
            embed.add_field(name="🧶 Crafting", value="`!unlock` - Buy new machine to get rich" \
            "\n`!upgrade` -  Gotta upgrade those machines don't we?", inline=False)
            embed.add_field(
    name="🛠️ Jobs",
    value="`!work` - Perform jobs like knight, digger, miner, or thief to earn resources.",
    inline=False
)
            embed.add_field(name="🙋🏻‍♀️ Help", value="`!commandhelp` - Look down, bottom of this embed 👇🏻", inline=False)
            embed.add_field(name="📚 Guides", value="`!details` - Open a detailed, paginated guide for a system (battle, jobs, loadout, race).", inline=False)
            embed.add_field(name="🐐 Profile", value="`!helloVeyra` - HIIIIII!!")
            embed.set_footer(text="Use !commandhelp <command> for more info on a particular command.")

        else:
            embed = discord.Embed(
                title="⚡ Slash Commands",
                description="Use these commands directly by typing `/`.",
                color=discord.Color.green()
            )
            embed.add_field(name="🎲 Games", value="`/battle` - Challenge anyone to a turn-based PvP battle.\n"
                                                  "`/start_race` - Start an animal race and bet your gold to win more!!!", inline=False)
            embed.add_field(name="💸 Economy", value="`/transfer_gold` - Send your gold to your friends :O", inline=False)
            embed.add_field(name="㊗️ Wordle", value="`/wordle_hint` - Get a hint if you just can't guess the next word.", inline=False)
            embed.add_field(name="📦 Inventory", value="`/transfer_item` - Give items from your inventory to your friends." \
                                         "`/quest` - Maybe I need some items? Check it out — you’ll be rewarded for helping!" ,inline=False)
            embed.add_field(name="🛍️ Shop and Marketplace", value="`/shop` - View the shop embed. Check what items I'm selling and buying.\n"
                                                                  "`/create_listing` - Create a marketplace listing others can buy at the price you set.\n"
                                                                  "`/load_marketplace` - See what others (and you) are selling.\n"
                                                                  "`/buy_from_marketplace` - Like something in the marketplace? Make it yours if you've got the gold!" \
                                                                  "`/delete_listing` - Delete one of your active listings.", inline=False)
            embed.add_field(name="🔥 Smelting", value="`/smelt` - Turn your ores into bars", inline=False)
            embed.add_field(name="📈 Leaderboard", value="`/leaderboard` - Check who currently has the most gold.", inline=False)
            embed.add_field(name="🧾 Profile", value="`/profile` - View your full Veyra profile.", inline=False)
            embed.add_field(name="🙋🏻 Help", value="`/help` - Well, you just used it, didn’t you?")
            embed.set_footer(text="Use !commandhelp <command> for more info on a particular command.")

        # Update button states
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                if child.custom_id == "prefix":
                    child.disabled = self.current_page == "prefix"
                elif child.custom_id == "slash":
                    child.disabled = self.current_page == "slash"

        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Prefix Commands", style=discord.ButtonStyle.blurple, custom_id="prefix")
    async def prefix_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.current_page = "prefix"
        await self.update_embed(interaction)

    @discord.ui.button(label="/ Commands", style=discord.ButtonStyle.green, custom_id="slash")
    async def slash_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.current_page = "slash"
        await self.update_embed(interaction)

    async def on_timeout(self):
        # Disable all buttons after timeout
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True
        try:
            await self.message.edit(view=self)
        except Exception:
            pass

def get_help_embed(user: discord.User):
    view = HelpView(user=user)
    embed = discord.Embed(
        title="📜 Prefix Commands",
        description="Use these commands with `!` before the command name.\n\n**Example:** `!checkwallet`, `!quest`",

        color=discord.Color.blurple()
    )
    embed.add_field(name="🔥 Stats", value="`!check` - View your different stats", inline=False)
    embed.add_field(name="😶‍🌫️ Gambling", value="`!bet` - Place your bets during active races.", inline=False)
    embed.add_field(name="🎲 Fun", value="`!ping` - The legendary ping-pong game.\n"
                                         "`!solve_wordle` - Let me solve your Wordle if the hints aren’t enough, cutie"
                                         "\n`!play` - We can play a number guessing game :3"
                                         "\n`!flipcoin` - Let gacha decide your fate", inline=False)
    embed.add_field(name="🗃️ Inventory", value="`!info` - Confused? I can tell you about any item — just name it!" \
    "\n`!use` - Use any usable item from your inventory.", inline=False)
    embed.add_field(name="😵‍💫 Lootbox", value="`!open` - Got boxes? I can open them for you :3", inline=False)
    embed.add_field(name="🛒 Shop", value="`!buy` - Purchase anything available in today’s shop.\n"
                                         "`!sell` - Sell your items if they’re in the buyback section.", inline=False)
    embed.add_field(name="🧶 Crafting", value="`!unlock` - Buy new machine to get rich"
                                             "\n`!upgrade` - Upgrade machines for better gains",
                                              inline=False)
    embed.add_field(
    name="🛠️ Jobs",
    value="`!work` - Perform jobs like knight, digger, miner, or thief to earn resources.",
    inline=False
)
    embed.add_field(name="📚 Guides", value="`!details` - Open a detailed, paginated guide for a system (battle, jobs, loadout, race).", inline=False)
    embed.add_field(name="🐐 Profile", value="`!helloVeyra` - HIIIIII!!")
    embed.set_footer(text="Use !commandhelp <command> for more info on a particular command.")
    return embed, view

def get_command_info_embed(command_name: str):

    HELP_DATA = load_json(os.path.join(os.path.dirname(__file__),"helpdata", "commandsinfo.json"))

    command_data = HELP_DATA.get(command_name.lower())

    if not command_data:
        embed = discord.Embed(
            title="❌ Command Not Found",
            description=f"The command `{command_name}` does not exist or is unknown. Please check the command name and try again.",
            color=discord.Color.red()
        )
        return embed

    embed = discord.Embed(
        title=command_data.get('title', command_name),
        description=command_data.get('description', "No description available."),
        color=discord.Color.blurple()
    )
    usage = command_data.get('usage')
    if usage:
        embed.add_field(name="Usage", value=f"`{usage}`", inline=False)
    category = command_data.get('category')
    if category:
        embed.add_field(name="Category", value=category, inline=True)
    cooldown = command_data.get('cooldown')
    if cooldown:
        embed.add_field(name="Cooldown", value=cooldown, inline=True)
    examples = command_data.get('examples')
    if examples:
        if isinstance(examples, list):
            examples_text = "\n".join(f"`{ex}`" for ex in examples)
        else:
            examples_text = f"`{examples}`"
        embed.add_field(name="Examples", value=examples_text, inline=False)
    notes = command_data.get('notes')
    if notes:
        embed.add_field(name="Notes", value=notes, inline=False)

    return embed


def _color_from_name(name: str):
    name = (name or "").lower()
    return {
        "blurple": discord.Color.blurple(),
        "green": discord.Color.green(),
        "red": discord.Color.red(),
        "gold": discord.Color.gold(),
        "purple": discord.Color.purple(),
        "orange": discord.Color.orange(),
        "blue": discord.Color.blue(),
        "pink": discord.Color.magenta(),
    }.get(name, discord.Color.blurple())



def build_page_embed(data: dict, page_index: int):
    pages = data.get("pages", [])
    page = pages[page_index]

    embed = discord.Embed(
        title=page.get("title") or data.get("title", "Help"),
        description=page.get("description", ""),
        color=_color_from_name(data.get("color", "blurple"))
    )

    # fields
    for field in page.get("fields", []):
        embed.add_field(
            name=field.get("name", "\u200b"),
            value=field.get("value", "\u200b"),
            inline=field.get("inline", False)
        )

    footer_base = data.get("footer", "")
    embed.set_footer(text=f"{footer_base} • Page {page_index+1}/{len(pages)}".strip(" • "))

    return embed


class JSONPageView(discord.ui.View):
    def __init__(self, user: discord.User, data: dict):
        super().__init__(timeout=300)
        self.user = user
        self.data = data
        self.page = 0

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("❌ Not your embed lil bro.", ephemeral=True)
            return False
        return True

    def _update_buttons(self):
        total = len(self.data["pages"])
        self.prev_button.disabled = (self.page == 0)
        self.next_button.disabled = (self.page == total - 1)

    @discord.ui.button(emoji="◀️", style=discord.ButtonStyle.gray)
    async def prev_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.page -= 1
        self._update_buttons()
        await interaction.response.edit_message(embed=build_page_embed(self.data, self.page), view=self)

    @discord.ui.button(emoji="▶️", style=discord.ButtonStyle.gray)
    async def next_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.page += 1
        self._update_buttons()
        await interaction.response.edit_message(embed=build_page_embed(self.data, self.page), view=self)


DETAILS_MAP = {
        "battle": "battle.json",
        "jobs": "jobs.json",
        "loadout": "loadout.json",
        "race": "race.json",
        "smelting": "smelt.json",
        "inventory": "inventory.json",
        "gambling": "gambling.json",
        "loan": "loan.json"
    }

def get_json_pages_embed(user: discord.User, topic: str):

    mapped_file = DETAILS_MAP.get(topic)

    if not mapped_file:
        embed = discord.Embed(
            title="❌ No such system",
            description="Try `!details race` \n allowed arguments: battle, jobs, loadout, race, smelting, inventory, gambling, loan",
            color=discord.Color.red()
        )
        return embed, None

    SYSTEM_DETAIL = load_json(
    os.path.join(os.path.dirname(__file__), "helpdata", mapped_file)
)
    # guard
    if not SYSTEM_DETAIL.get("pages"):
        embed = discord.Embed(
            title="❌ No pages",
            description="Your JSON has no `pages` array.",
            color=discord.Color.red()
        )
        return embed, None

    view = JSONPageView(user, SYSTEM_DETAIL)
    view._update_buttons()

    embed = build_page_embed(SYSTEM_DETAIL, 0)
    return embed, view