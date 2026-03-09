import discord
from discord.ext import commands

import os, json

_HELP_JSON_CACHE = {}

def load_json(path: str):
    if path not in _HELP_JSON_CACHE:
        with open(path, "r", encoding="utf-8") as f:
            _HELP_JSON_CACHE[path] = json.load(f)
    return _HELP_JSON_CACHE[path]


def _normalize_command_key(command_name: str) -> str:
    """Normalize command input so users can pass with or without ! or /."""
    key = (command_name or "").strip().lower()
    if key.startswith("/") or key.startswith("!"):
        key = key[1:]
    return " ".join(key.split())


def get_all_commandhelp_options() -> list[str]:
    help_data = load_json(os.path.join(os.path.dirname(__file__), "helpdata", "commandsinfo.json"))
    return sorted(help_data.keys())


def build_prefix_help_embed() -> discord.Embed:
    embed = discord.Embed(
        title="📘 Veyra Prefix Commands",
        description="Use `!` commands for quick actions.",
        color=discord.Color.blurple()
    )

    embed.add_field(
        name="🎮 Games",
        value="`!ping` - Bot latency check\n"
              "`!flipcoin` - Flip a coin\n"
              "`!play` - Number guessing game\n"
              "`!solve_wordle` - Start Wordle solver session",
        inline=False
    )
    embed.add_field(
        name="🎒 Inventory & Loot",
        value="`!info <item_name>` - Item info\n"
              "`!use <item_name>` - Use an item\n"
              "`!open <lootbox_name>` - Open a lootbox",
        inline=False
    )
    embed.add_field(
        name="🛒 Economy & Shop",
        value="`!buy <item_name> [amount]` - Buy from shop\n"
              "`!sell <item> <amount>` - Sell to buyback\n"
              "`!buychips <pack_id>` - Convert gold to chips\n"
              "`!cashout <pack_id>` - Convert chips to gold\n"
              "`!repayloan` - Repay active loan",
        inline=False
    )
    embed.add_field(
        name="🛠️ Progression",
        value="`!unlock <building_name>` - Unlock machine/building\n"
              "`!upgrade <building_name>` - Upgrade building\n"
              "`!bet <animal> <amount>` - Bet in active race",
        inline=False
    )
    embed.add_field(
        name="🙋 Help & Profile",
        value="`!helloVeyra` - Check your friendship status\n"
              "`/commandhelp <command_name>` - Command docs",
        inline=False
    )
    embed.set_footer(text="Tip: Use /help and switch to / Commands for slash commands.")
    return embed


def build_slash_help_embed() -> discord.Embed:
    embed = discord.Embed(
        title="✨ Veyra Slash Commands",
        description="Use `/` commands for full features and interactive UIs.",
        color=discord.Color.green()
    )

    embed.add_field(
        name="⚔️ Battle",
        value="`/battle <target> <bet>` - PvP battle\n"
              "`/campaign [delay]` - PvE campaign fight\n"
              "`/loadout` - Set weapon + spell\n"
              "`/open_to_battle <min_bet> <max_bet>` - Join auto-match queue",
        inline=False
    )
    embed.add_field(
        name="🧪 Crafting",
        value="`/smelt <bar_name> <amount>` - Smelt ores into bars\n"
              "`/brew <potion_name>` - Brew a potion",
        inline=False
    )
    embed.add_field(
        name="💰 Economy",
        value="`/leaderboard` - Richest players\n"
              "`/loan` - Claim starter loan\n"
              "`/transfer_gold <user> <amount>` - Send gold",
        inline=False
    )
    embed.add_field(
        name="🎲 Games & Quests",
        value="`/start_race` - Start race event\n"
              "`/quest` - View, skip, claim, or refresh quest\n"
              "`/wordle_hint` - Wordle hint from guess history\n"
              "`/gamble flipcoin|roulette|slots|dungeon` - Casino minigames",
        inline=False
    )
    embed.add_field(
        name="🎒 Inventory & Market",
          value="`/transfer_item <user> <item_name> <amount>` - Send item\n"
              "`/find_item <item_name>` - Where to get item\n"
              "`/shop` - Open shop\n"
              "`/create_listing <item_name> <quantity> <price>` - List item\n"
              "`/loadmarketplace` - Browse listings\n"
              "`/buy_from_marketplace <listing_id> <quantity>` - Buy listing\n"
              "`/delete_listing <listing_id>` - Remove your listing",
        inline=False
    )
    embed.add_field(
        name="💼 Work & Checks",
        value="`/work knight|digger|miner|explorer` - Do jobs\n"
              "`/work thief <target>` - Attempt a steal\n"
              "`/check wallet|energy|inventory|exp|smelter|brewing_stand|pockets|status` - Quick stat checks",
        inline=False
    )
    embed.add_field(
        name="👤 Utility",
        value="`/casino` - Open casino menu\n"
              "`/help` - Open this menu\n"
              "`/details <topic>` - System guides\n"
              "`/introduction` - Intro modal\n"
              "`/profile` - View profile\n"
              "`/invite` - Referral progress",
        inline=False
    )
    embed.set_footer(text="Need specifics? Use !commandhelp <command>.")
    return embed

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
            embed = build_prefix_help_embed()

        else:
            embed = build_slash_help_embed()

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
    embed = build_prefix_help_embed()
    return embed, view

def get_command_info_embed(command_name: str):

    HELP_DATA = load_json(os.path.join(os.path.dirname(__file__),"helpdata", "commandsinfo.json"))

    command_key = _normalize_command_key(command_name)
    command_data = HELP_DATA.get(command_key)

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
    "quests": "quests.json",
        "jobs": "jobs.json",
        "loadout": "loadout.json",
        "race": "race.json",
        "smelting": "smelt.json",
        "inventory": "inventory.json",
        "gambling": "gambling.json",
        "loan": "loan.json",
        "alchemy": "alchemy.json",
        "potions": "potions.json"
    }

def get_json_pages_embed(user: discord.User, topic: str):

    mapped_file = DETAILS_MAP.get(topic)

    if not mapped_file:
        embed = discord.Embed(
            title="❌ No such system",
            description="Try `!details race` \n allowed arguments: battle, quests, jobs, loadout, race, smelting, inventory, gambling, loan, alchemy, potions",
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