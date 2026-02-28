import random

from discord.ext import commands
import asyncio


from utils.solver import init_wordle, update_wordle, build_state_from_history,suggest_next_guess
from utils.global_sessions_registry import sessions
from utils.custom_errors import VeyraError,WrongInputError
from utils.embeds.questembed import create_quest_embed


from services.delievry_minigame_services import requested_items
from services.guessthenumber_services import Guess
from services.response_services import create_response

from domain.guild.commands_policies import non_spam_command

class Games(commands.Cog):

    def __init__(self,bot):
        self.bot=bot
        self.wordle_sessions = sessions["wordle"]
        self.guess_sessions = sessions["guess"]

    @commands.command()
    async def ping(self,ctx):
        """The legendary Ping-Pong game"""
        await ctx.send("🏓Pong!")

    @commands.command()
    @non_spam_command()
    async def flipcoin(self, ctx):
        result = random.choice(["head", "tail"])
        response = create_response("flipcoin", 1, result=result)
        await ctx.send(response)

    @commands.command()
    async def solve_wordle(self, ctx):
        """Solve wordle"""
        # prevent duplicate sessions per user
        if ctx.author.id in self.wordle_sessions:
            await ctx.send("⚠️ You already have an active Wordle game running! Finish that one first. :)")
            return

        msg = await ctx.send("Solving a Wordle game...")

        thread = await msg.create_thread(
            name=f"{ctx.author.name}'s Wordle"
        )
        await thread.send(
    "**How this works:**\n"
    "I'll drop you guesses. You input them into Wordle and reply with results.\n\n"
    "**Example:** If I guess `Cutie`, and you get:\n"
    "> C → 🟩 Green\n"
    "> U → 🟨 Yellow\n"
    "> T → ⬜ White\n"
    "> I → ⬜ White\n"
    "> E → 🟩 Green\n\n"
    "**You reply with:** `21002`\n"
    "`0` = white, `1` = yellow, `2` = green.\n\n"
    "Don't mess up the inputs and you win :3"
)

        with open("wordle.txt") as f:
            words = [w.strip() for w in f]

        state = init_wordle(words)
        self.wordle_sessions[ctx.author.id] = state

        while self.wordle_sessions.get(ctx.author.id, {}).get("attempts", 0) > 0 and self.wordle_sessions[ctx.author.id].get("guess"):
            guess = self.wordle_sessions[ctx.author.id]["guess"]
            await thread.send(f"Guess: {guess}")  # <- send in thread now

            def check(msg):
                return msg.author == ctx.author and msg.channel == thread  # <- also check inside thread

            try:
                msg = await self.bot.wait_for("message", check=check, timeout=130)
                result = msg.content.strip()
            except asyncio.TimeoutError:
                await thread.send("Too slow, try again later.")
                del self.wordle_sessions[ctx.author.id]
                return
            except WrongInputError as e:
                await thread.send(e)

            if result == "22222":
                await thread.send("Congratulations 🎉")
                del self.wordle_sessions[ctx.author.id]
                return

            self.wordle_sessions[ctx.author.id], _ = update_wordle(self.wordle_sessions[ctx.author.id], result)

        await thread.send("Game over! You're out of attempts.")
        del self.wordle_sessions[ctx.author.id]


    @commands.slash_command(name="wordle_hint", description="Get a Wordle hint based on your past guesses and feedbacks")
    async def wordle_hint(self, ctx,
        guess1: str = None, pattern1: str = None,
        guess2: str = None, pattern2: str = None,
        guess3: str = None, pattern3: str = None,
        guess4: str = None, pattern4: str = None,
        guess5: str = None, pattern5: str = None,
    ):
        await ctx.defer()

        with open("wordle.txt") as f:
            words = [w.strip() for w in f]

        history = []
        for i in range(1, 6):
            guess = locals().get(f"guess{i}")
            pattern = locals().get(f"pattern{i}")
            if guess and pattern:
                if len(guess) != 5 or len(pattern) != 5 or not all(c in "012" for c in pattern):
                    await ctx.respond(f"Invalid input in guess{i} or pattern{i}. Make sure it's 5 letters and pattern uses only 0, 1, 2. \n0 for white, 1 for yellow, for green")
                    return
                history.append((guess.lower(), pattern))

        if not history:
            await ctx.respond("What do you want me to guess from?? air??? Well I can guess from void as well use `!solve_wordle` if you wanna do that")
            return

        try:
            state = build_state_from_history(words, history)
            hint = suggest_next_guess(state)
            await ctx.respond(f"Try: *{hint.upper()}*")
        except Exception as e:
            await ctx.respond(f"Error generating hint: {str(e)}")

    @commands.slash_command(name = "quest", description="Do quest for Veyra")
    async def quest(self,ctx):
        embed, view = requested_items(ctx.author.display_name, ctx.author.id)
        await ctx.respond(embed=embed, view=view)

    @commands.command()
    async def play(self, ctx):
        guess = Guess()
        await guess.play_game(ctx, self.bot, self.guess_sessions)

    @commands.slash_command(name="task", description="View a sample task")
    async def task(self, ctx):

        dummy_quest = {
            "name": "Defeat the Dragon",
            "description": "Travel to the mountains and defeat the ancient dragon",
            "reward": 500
        }

        dummy_progress = {
            "current": 7,
            "total": 10,
        }

        embed = create_quest_embed(dummy_quest, dummy_progress)
        await ctx.respond(embed=embed)


def setup(bot):
    """Setup the Cog"""
    bot.add_cog(Games(bot))