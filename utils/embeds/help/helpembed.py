import discord
from discord.ext import commands

import os, json

file_path = os.path.join(os.path.dirname(__file__), "commandsinfo.json")
with open(file_path, "r", encoding="utf-8") as f:
    HELP_DATA = json.load(f)

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
                description="Use these commands with `!` before the command name.\nAll commands are case-insensitive except for `!helloVeyra`\n\n**Example:** `!balance`, `!shop`",
                color=discord.Color.blurple()
            )
            embed.add_field(name="💰 Economy", value="`!checkwallet` - Check how much stash you've got!", inline=False)
            embed.add_field(name="🔥 Exp", value="`!checkexp` - See your current level along with your experience points.", inline=False)
            embed.add_field(name="😶‍🌫️ Gambling", value="`!bet` - Place your bets if there's an ongoing race.", inline=False)
            embed.add_field(name="🎲 Fun", value="`!ping` - The legendary ping-pong game.\n"
                                                 "`!solve_wordle` - Let me solve the entire Wordle for you if the hints aren't enough, cutie :3\n"
                                                 "`!quest` - Maybe I need some items? Why not check it out? You'll be rewarded for your efforts!" \
                                                 "\n`!play - We can play a number guess game :3`", inline=False)
            embed.add_field(name="🗃️ Inventory", value="`!checkinventory` - See what items you have and how many." \
            "\n`!info - Confused? I can tell you about anyitem just name it.`", inline=False)
            embed.add_field(name="😵‍💫 Lootbox", value="`!open` - Got boxes? I can open them for you :3", inline=False)
            embed.add_field(name="🛒 Shop", value="`!buy` - Purchase anything from the currently active shop.\n"
                                                  "`!sell` - Sell your items if they're in the buyback shop.", inline=False)
            embed.add_field(name="🙋🏻‍♀️ Help", value="`!commandhelp - Look down, bottom of this embed 👇🏻`", inline= False)
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
            embed.add_field(name="📦 Inventory", value="`/transfer_item` - Give items from your inventory to your friends.", inline=False)
            embed.add_field(name="🛍️ Shop and Marketplace", value="`/shop` - View the shop embed. Check what items I'm selling and buying.\n"
                                                                  "`/create_listing` - Create a marketplace listing others can buy at the price you set.\n"
                                                                  "`/load_marketplace` - See what others (and you) are selling.\n"
                                                                  "`/buy_from_marketplace` - Like something in the marketplace? Make it yours if you've got the gold!" \
                                                                  "`/delete_listing - Delete one of your active listings.`", inline=False)
            embed.add_field(name="🙋🏻 Help", value="`/help` - Well, you just used it, didn't you??")

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
        except:
            pass

def get_help_embed(user: discord.User):
    view = HelpView(user=user)
    embed = discord.Embed(
        title="📜 Prefix Commands",
        description="Use these commands with `!` before the command name.\nAll commands are case-insensitive except for `!helloVeyra`\n\n**Example:** `!balance`, `!shop`",

        color=discord.Color.blurple()
    )
    embed.add_field(name="💰 Economy", value="`!checkwallet` - Check how much stash you've got!", inline=False)
    embed.add_field(name="🔥 Exp", value="`!checkexp` - See your current level along with your experience points.", inline=False)
    embed.add_field(name="😶‍🌫️ Gambling", value="`!bet` - Place your bets if there's an ongoing race.", inline=False)
    embed.add_field(name="🎲 Fun", value="`!ping` - The legendary ping-pong game.\n"
                                         "`!solve_wordle` - Let me solve the entire Wordle for you if the hints aren't enough, cutie :3\n"
                                         "`!quest` - Maybe I need some items? Why not check it out? You'll be rewarded for your efforts!", inline=False)
    embed.add_field(name="🗃️ Inventory", value="`!checkinventory` - See what items you have and how many.", inline=False)
    embed.add_field(name="😵‍💫 Lootbox", value="`!open` - Got boxes? I can open them for you :3", inline=False)
    embed.add_field(name="🛒 Shop", value="`!buy` - Purchase anything from the currently active shop.\n"
                                         "`!sell` - Sell your items if they're in the buyback shop.", inline=False)
    embed.add_field(name="🐐 Profile", value="`!helloVeyra` - HIIIIII!!")
    embed.set_footer(text="Use !commandhelp <command> for more info on a particular command.")
    return embed, view

def get_command_info_embed(command_name: str):
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
