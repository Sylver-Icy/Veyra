"""Cog module for managing gambling-related commands, including starting animal races and placing bets."""
import discord
from discord.ext import commands
import asyncio
from rapidfuzz import process, fuzz

from services.race_services import start_race, add_bets
from services.economy_services import remove_gold, add_gold
from services.casino_services import play_casino_game, GAMES

from utils.embeds.animalraceembed import race_start_embed
from utils.embeds.casinoembed import animate_casino_result
from utils.custom_errors import NotEnoughGoldError
from utils.fuzzy import normalize_game_name

from domain.guild.commands_policies import non_spam_command

class Gambling(commands.Cog):
    """Cog for handling gambling commands such as starting races and placing bets."""

    gamble = discord.SlashCommandGroup(
        "gamble",
        "Play casino games"
    )

    def __init__(self, bot):
        """
        Initialize the Gambling cog.

        Args:
            bot: The discord bot instance.
        """
        self.bot = bot
        # Flag to indicate whether betting is currently allowed
        self.betting_phase = False


    @gamble.command(name="flipcoin", description="Bet on a coin flip")
    async def gamble_flipcoin(
        self,
        ctx: discord.ApplicationContext,
        bet: discord.Option(int, "Amount of gold to bet", min_value=1, max_value=5000),
        choice: discord.Option(str, "Pick heads or tails", choices=["Heads", "Tails"])
    ):
        data = play_casino_game(ctx.author.id, "flipcoin", bet, choice)
        await animate_casino_result(ctx.interaction, data)

    @gamble.command(name="roulette", description="Bet on a roulette number")
    async def gamble_roulette(
        self,
        ctx: discord.ApplicationContext,
        bet: discord.Option(int, "Amount of gold to bet", min_value=10, max_value=2500),
        number: discord.Option(int, "Choose a number (0–9)", min_value=0, max_value=9)
    ):
        data = play_casino_game(ctx.author.id, "roulette", bet, str(number))
        await animate_casino_result(ctx.interaction, data)

    @gamble.command(name="slots", description="Spin the slot machine")
    async def gamble_slots(
        self,
        ctx: discord.ApplicationContext,
        bet: discord.Option(int, "Amount of gold to bet", min_value=10, max_value=2000)
    ):
        data = play_casino_game(ctx.author.id, "slots", bet, "")
        await animate_casino_result(ctx.interaction, data)

    @gamble.command(name="dungeon", description="Risk gold exploring a dungeon")
    async def gamble_dungeon(
        self,
        ctx: discord.ApplicationContext,
        bet: discord.Option(int, "Amount of gold to risk", min_value=10, max_value=3000),
        area: discord.Option(str, "Choose a dungeon", choices=["Caves", "Tunnels", "Ruins", "Lair", "Abyss"])
    ):
        data = play_casino_game(ctx.author.id, "dungeon", bet, area)
        await animate_casino_result(ctx.interaction, data)


    @commands.slash_command(name="start_race", description="Start an animal race and bet on the animals")
    @commands.cooldown(1,900, commands.BucketType.guild)
    @non_spam_command()
    async def start_race(self, ctx):
        """
        Slash command to start an animal race.

        This command initiates the betting phase, sends an embed with race info,
        waits for the betting period (180 seconds), then closes betting and starts the race.

        Cooldown:
            Limited to once every 900 seconds per guild to prevent spam.

        Args:
            ctx: The context of the command invocation.
        """
        # Enable betting phase so users can place bets
        self.betting_phase = True

        # Generate and send race start embed and mentions
        embed, mentions = race_start_embed(ctx.author)
        role = discord.utils.get(ctx.guild.roles, name="Betters")

        allowed_mentions = discord.AllowedMentions(roles=True, users=True, everyone=False)

        if role:
            await ctx.respond(
                content=f"{mentions} {role.mention}",
                embed=embed,
                allowed_mentions=allowed_mentions
            )
        else:
            await ctx.respond(content=mentions, embed=embed, allowed_mentions=allowed_mentions)

        # Wait for betting phase duration (180 seconds)
        await asyncio.sleep(180)  # 3minutes

        # Disable betting phase to prevent further bets
        self.betting_phase = False

        # Notify users that betting is closed and race is starting
        await ctx.respond("Betting is now closed. The race begins!")

        # Start the race logic
        await start_race(ctx)
        return

    @commands.command()
    @non_spam_command()
    async def bet(self, ctx, animal: str, bet: str):
        """
        Command to place a bet on an animal in the ongoing race.

        Validates the animal choice and bet amount, checks if betting is open,
        deducts gold from the user, and registers the bet.

        Args:
            ctx: The context of the command invocation.
            animal: The animal to bet on (e.g., rabbit, turtle, fox).
            bet: The amount of gold to bet as a string.
        """
        valid_animals = ["rabbit", "turtle", "fox"]

        # Validate animal choice
        if animal.lower() not in valid_animals:
            await ctx.send("Our competing candidates are Rabbit, Turtle, and Fox. Please bet only on them.")
            return

        # Validate bet amount is an integer
        try:
            bet = int(bet)
        except ValueError:
            await ctx.send("Please enter a valid number for your bet.")
            return

        # Validate bet amount is positive
        if bet <= 0:
            await ctx.send("Invalid bet amount.")
            return

        # Check if betting phase is active
        if self.betting_phase:
            try:
                # Attempt to deduct gold from user's balance
                remove_gold(ctx.author.id, bet)
            except NotEnoughGoldError:
                # Inform user if they lack sufficient funds
                await ctx.send("You don't have enough money to bet maybe try betting less?")
                return

            # Try to add the bet to the race system
            success = add_bets(ctx.author.id, animal.lower(), bet)
            if success:
                # Confirm bet placement to the user
                await ctx.send(f"You placed your bet on **{animal.capitalize()}** for **{bet}** gold! Let's pray they run fast 🏁")
            else:
                # Refund gold if user already has a bet and cannot change it
                add_gold(ctx.author.id, bet) #refund the gold deducted earlier
                await ctx.send("You already have a bet. Can't change")
        else:
            # Inform user that betting is currently closed
            await ctx.send("There is no ongoing betting phase right now.")

def setup(bot):
    """Setup function to add the Gambling cog to the bot."""
    bot.add_cog(Gambling(bot))