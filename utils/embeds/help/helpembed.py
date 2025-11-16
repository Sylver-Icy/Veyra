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
        except:
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



def battle_guide_embed():
    """
    Returns a detailed, structured Discord embed explaining how the battle system works.
    Designed to help new players understand the flow, stats, and strategies in a formal yet clear way.
    """
    embed = discord.Embed(
        title="⚔️ Veyra Battle Guide",
        description=(
            "This guide explains how the **1v1 Battle System** works in Veyra. "
            "Battles are turn-based encounters where two players face off using a mix of **strategy, prediction, and stats**.\n\n"
            "Each round, both players secretly choose an action — known as a **stance** — and the outcome is resolved based on their stats and the interactions between their moves."
        ),
        color=discord.Color.purple()
    )

    # ─── 1. How to Start a Battle ────────────────────────────────────────────
    embed.add_field(
        name="🧩 How to Start a Battle",
        value=(
            "• Use `/battle @user <bet>` to challenge another player.\n"
            "• Both players must have enough gold to place the bet.\n"
            "• The challenged player can accept or reject the duel.\n"
            "• If accepted, both sides' bet amount is locked as the **pot**, and the match begins.\n\n"
            "**Victory Rewards:** The winner receives 90% of the total pot (Veyra takes a 10% cut)."
        ),
        inline=False
    )

    # ─── 2. Core Stats ───────────────────────────────────────────────────────────────
    embed.add_field(
        name="📊 Core Stats Explained",
        value=(
            "**Attack:** Determines your damage output. Increases slightly every time you successfully hit.\n"
            "**Defense:** Reduces incoming damage. Can increase through successful blocks.\n"
            "**Speed:** Determines action order and affects block/counter success.\n"
            "**HP (Health):** When it reaches 0, you’re out. Simple as that.\n"
            "**Mana:** Required to cast spells. Some actions may drain or regenerate mana."
        ),
        inline=False
    )

    # ─── 3. Available Stances ───────────────────────────────────────────────
    embed.add_field(
        name="🎭 Battle Stances (Actions You Can Take Each Round)",
        value=(
            "Each round, you must choose **one** of the following stances:\n\n"
            "**⚔️ Attack:** Deal direct damage based on your Attack stat. "
            "If you hit an unguarded opponent, you’ll deal more damage and slightly increase your Attack permanently.\n\n"
            "**🛡️ Block:** Reduce incoming damage by 70% if timed correctly. "
            "A successful block also boosts your Defense slightly, but failing it may reduce your Defense or HP.\n\n"
            "**🔁 Counter:** Reflect 50% of the incoming attack back at your opponent if they attack. "
            "If your prediction is wrong, you’ll suffer Defense/Speed debuffs or HP loss.\n\n"
            "**💧 Recover:** Regain HP or Mana if the opponent is defensive (block/counter). "
            "If they attack instead, your recovery is interrupted, and you’ll take damage.\n\n"
            "**🔮 Cast:** Spend 15 Mana to unleash one of four random spells: "
            "_Fireball_, _Poison_, _Nightfall_, or _Heavyshot_. Each has a unique effect."
        ),
        inline=False
    )

    # ─── 4. Spell Effects ───────────────────────────────────────────────
    embed.add_field(
        name="✨ Spell Effects",
        value=(
            "**🔥 Fireball:** Deals 24 flat damage instantly.\n"
            "**☠️ Poison:** Applies a status effect that deals 4 HP damage every round.\n"
            "**🌑 Nightfall:** Reduces a random stat (Attack, Speed, Mana, or HP) by 2 every round.\n"
            "**💥 Heavyshot:** Sets your opponent’s HP equal to your own (massive risk–reward spell)."
        ),
        inline=False
    )

    # ─── 5. Status Effects ───────────────────────────────────────────────
    embed.add_field(
        name="☠️ Status Effects & Penalties",
        value=(
            "**Poisoned:** You lose 4 HP every round until it fades.\n"
            "**Nightfall:** Randomly drains one stat by 2 points per round.\n"
            "**Timeout Penalty:** If you take too long to pick a move, you automatically Attack but lose 25 HP as a penalty."
        ),
        inline=False
    )

    # ─── 6. Round Flow ───────────────────────────────────────────────
    embed.add_field(
        name="🔁 Battle Flow (Round-by-Round)",
        value=(
            "1️⃣ Both players pick a stance using buttons.\n"
            "2️⃣ Once both have locked in, the engine resolves the round based on stats and move interactions.\n"
            "3️⃣ Any poison or nightfall effects are processed.\n"
            "4️⃣ The next round begins automatically after a short delay.\n"
            "5️⃣ The battle ends immediately when one (or both) players reach 0 HP."
        ),
        inline=False
    )

    # ─── 7. Strategy Tips ───────────────────────────────────────────────
    embed.add_field(
        name="🧠 Strategy Tips",
        value=(
            "• Watch your **speed** closely — it affects blocking and turn order.\n"
            "• Alternate between offensive and defensive stances to stay unpredictable.\n"
            "• Don’t spam Attack — smart players will Counter.\n"
            "• Save Mana for critical moments. Casting early can leave you defenseless.\n"
            "• Block and Recover are safer options when your HP is low.\n"
            "• Keep an eye on your opponent’s patterns — most people repeat habits."
        ),
        inline=False
    )

    # ─── 8. End Conditions ───────────────────────────────────────────────
    embed.add_field(
        name="🏁 How Battles End",
        value=(
            "A match ends when:\n"
            "• One player’s HP drops to 0 → the other wins and earns 90% of the pot.\n"
            "• Both die in the same round → the battle is declared a draw, and bets are refunded.\n\n"
            "Each battle round has a **50-second timer** — failure to choose a move results in automatic penalties."
        ),
        inline=False
    )

    # ─── Footer ───────────────────────────────────────────────
    embed.set_footer(
        text="Master the mind games. Every move counts — predict, adapt, and conquer."
    )

    return embed


def race_guide_embed():
    """
    Returns a detailed, formal Discord embed explaining the Animal Race system,
    written from Veyra’s perspective.
    """

    embed = discord.Embed(
        title="🏁 Veyra’s Animal Race — Complete Guide",
        description=(
            "Greetings, tester. I am **Veyra**, and this is my simulation known as the **Animal Race**.\n\n"
            "In this game, you will wager gold on one of three competitors as they race toward the finish line. "
            "It is a test of probability, risk management, and perhaps… misplaced faith.\n\n"
            "Allow me to explain how this system operates in detail."
        ),
        color=discord.Color.gold()
    )

    # 1. Overview
    embed.add_field(
        name="🎯 What the Race Is",
        value=(
            "Three contenders — 🐇 **Rabbit**, 🐢 **Turtle**, and 🦊 **Fox** — compete in a straight-line sprint of 30 tiles.\n"
            "Each turn, every participant advances a random distance between 1 and 4 steps. "
            "The first to cross the finish line is declared the victor.\n\n"
            "The process is entirely autonomous. Once initiated, I manage and broadcast the results live through embeds and commentary."
        ),
        inline=False
    )

    # 2. Starting the Race
    embed.add_field(
        name="🕒 Initiating a Race",
        value=(
            "A race begins when a user invokes `/start_race`.\n"
            "Once started, a **three-minute betting phase** opens. During this window, any registered participant may place a wager using:\n\n"
            "`!bet <animal> <amount>`\n"
            "Example: `!bet fox 200`\n\n"
            "After the timer expires, all bets are locked, and the race automatically begins. "
            "No further wagers or changes will be accepted at that point."
        ),
        inline=False
    )

    # 3. Betting Rules
    embed.add_field(
        name="💰 Betting Protocol",
        value=(
            "• Valid choices: `rabbit`, `turtle`, or `fox`.\n"
            "• Each user may place only **one** bet per race.\n"
            "• Your wagered gold is deducted instantly.\n"
            "• Changing or cancelling a bet is not permitted.\n"
            "• Insufficient balance will result in a failed transaction.\n\n"
            "Please verify your intent before confirming a bet — I am not responsible for impulsive decisions."
        ),
        inline=False
    )

    # 4. Race Flow
    embed.add_field(
        name="🏎️ Race Progression",
        value=(
            "Once the betting phase concludes, the race commences.\n"
            "Every few seconds, each animal’s position is recalculated based on random movement values. "
            "I continuously update the race embed so that all participants may observe the live progress.\n\n"
            "To maintain engagement, I occasionally broadcast commentary — brief messages that reflect current standings or random events. "
            "These messages are purely aesthetic and do not influence the outcome."
        ),
        inline=False
    )

    # 5. Reward Distribution
    embed.add_field(
        name="🏆 Reward Distribution",
        value=(
            "When a victor emerges, all users who wagered on that animal receive proportional payouts based on their contribution.\n\n"
            "**Calculation Formula:**\n"
            "`payout = (your_bet / total_bets_on_winner) × (total_pool × 0.9)`\n\n"
            "• I retain a **10% system fee** for maintenance purposes.\n"
            "• The prize pool consists of all bets combined.\n"
            "• If no participant placed a wager on the winning animal, no payouts occur."
        ),
        inline=False
    )

    # 6. Edge Cases
    embed.add_field(
        name="⚠️ Special Conditions",
        value=(
            "• In the rare event of a tie, the first animal registered as crossing the finish line is recognized as the winner.\n"
            "• If no bets were placed, the race still concludes, but no rewards are distributed.\n"
            "• After every race, all bet data is automatically cleared to prepare for the next session."
        ),
        inline=False
    )

    # 7. Strategy and Notes
    embed.add_field(
        name="🧠 Strategic Notes",
        value=(
            "• All movements are governed by random generation — skill plays no role here.\n"
            "• The turtle often appears slow but remains statistically equivalent to its competitors.\n"
            "• Large bets amplify both potential profit and loss. Wager wisely.\n"
            "• Pay attention to hype patterns; they may help you predict nothing at all, but humans find them entertaining."
        ),
        inline=False
    )

    # 8. Summary
    embed.add_field(
        name="📜 Summary",
        value=(
            "**Betting Duration:** 3 minutes\n"
            "**Race Duration:** 1–2 minutes (variable)\n"
            "**Finish Line:** 30 tiles\n"
            "**System Fee:** 10% of total prize pool\n\n"
            "Bet. Watch. Hope. And remember — in the end, probability always wins."
        ),
        inline=False
    )

    embed.set_footer(
        text="— Veyra"
    )

    return embed


# ─────────────────────────────────────────────────────────────────────────────
# JOB HELP PAGINATED VIEW
# Shows 1 job per page and auto-scales when new pages are added.
# ─────────────────────────────────────────────────────────────────────────────

JOB_PAGES = [
    {
        "title": "🛡️ Knight",
        "body": (
            "**Role:** Knights stand guard over Natlade, protecting travelers and maintaining peace.\n"
            "**Energy Cost:** 85\n"
            "**Reward:** 30–50 Gold"
        )
    },
    {
        "title": "⛏️ Digger",
        "body": (
            "**Role:** Diggers explore the outskirts, unearthing ancient boxes and forgotten treasures.\n"
            "**Energy Cost:** 70\n"
            "**Reward:** Lootboxes + occasional gold\n\n"
            "**Drop Rates:**\n"
            "• Gold: 29%\n"
            "• Wooden Box: 40%\n"
            "• Stone Box: 25%\n"
            "• Iron Box: 5%\n"
            "• Platinum Box: 1%"
        )
    },
    {
        "title": "⛏️ Miner",
        "body": (
            "**Role:** Miners descend into Natlade’s caves, gathering ores vital to the kingdom.\n"
            "**Energy Cost:** 50\n"
            "**Reward:** Gold + ores\n\n"
            "**Drop Rates:**\n"
            "• Gold: 10%\n"
            "• Coal: 20%\n"
            "• Copper Ore: 34%\n"
            "• Iron Ore: 24%\n"
            "• Silver Ore: 12%"
        )
    },
    {
        "title": "🗝️ Thief",
        "body": (
            "**Role:** Thieves sneak through Natlade, lifting pockets when luck allows.\n"
            "**Energy Cost:** 60\n"
            "**Success Chance:** 50%\n"
            "**Reward on Success:** Steal 10% of target's gold\n"
            "**Failure Penalty:** 30 Gold fine"
        )
    }
]

def job_page_embed(page_index: int):
    """
    Creates an embed for a single job page using JOB_PAGES data.
    """
    page = JOB_PAGES[page_index]
    embed = discord.Embed(
        title=page["title"],
        description=page["body"],
        color=discord.Color.orange()
    )
    embed.set_footer(text=f"Page {page_index + 1}/{len(JOB_PAGES)} • Use the buttons to navigate.")
    return embed


class JobHelpView(discord.ui.View):
    """
    Paginated button view to navigate between job pages.
    """
    def __init__(self, user: discord.User):
        super().__init__(timeout=300)
        self.user = user
        self.page = 0

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user.id:
            await interaction.response.send_message(
                "❌ Only the user who opened this can navigate pages.",
                ephemeral=True
            )
            return False
        return True

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.gray, custom_id="job_prev")
    async def previous_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.page = (self.page - 1) % len(JOB_PAGES)
        await interaction.response.edit_message(embed=job_page_embed(self.page), view=self)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.gray, custom_id="job_next")
    async def next_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.page = (self.page + 1) % len(JOB_PAGES)
        await interaction.response.edit_message(embed=job_page_embed(self.page), view=self)

    async def on_timeout(self):
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True
        try:
            await self.message.edit(view=self)
        except:
            pass


def get_job_help(user: discord.User):
    """
    Returns the first job page embed and its paginated view.
    """
    view = JobHelpView(user)
    embed = job_page_embed(0)
    return embed, view