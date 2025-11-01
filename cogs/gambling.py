"""Cog module for managing gambling-related commands, including starting animal races and placing bets."""

from discord.ext import commands
import asyncio
from services.race_services import start_race, add_bets
from services.economy_services import remove_gold, add_gold
from utils.embeds.animalraceembed import race_start_embed
from utils.custom_errors import NotEnoughGoldError

class Gambling(commands.Cog):
    """Cog for handling gambling commands such as starting races and placing bets."""

    def __init__(self, bot):
        """
        Initialize the Gambling cog.

        Args:
            bot: The discord bot instance.
        """
        self.bot = bot
        # Flag to indicate whether betting is currently allowed
        self.betting_phase = False

    @commands.slash_command()
    @commands.cooldown(1,900, commands.BucketType.guild)
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
        await ctx.respond(content = mentions, embed= embed)

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