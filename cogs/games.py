import random
from datetime import datetime

import discord
from discord.ext import commands
import asyncio


from utils.solver import init_wordle, update_wordle, build_state_from_history,suggest_next_guess
from utils.global_sessions_registry import sessions
from utils.custom_errors import VeyraError,WrongInputError
from utils.embeds.questembed import create_quest_embed, create_quest_complete_embed



from services.guessthenumber_services import Guess
from services.response_services import create_response

from services.quest_services import get_or_create_quest, skip_quest, claim_quest_rewards, create_quest
from database.sessionmaker import Session

from domain.guild.commands_policies import non_spam_command
from domain.quests.rules import get_quest_by_id


class SkipQuestView(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=120)
        self.user_id = user_id

    @discord.ui.button(label="Skip Quest", style=discord.ButtonStyle.danger, emoji="⏭️")
    async def skip_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your quest!", ephemeral=True)
            return

        with Session() as session:
            skipped = skip_quest(session, self.user_id)
            session.commit()

        if not skipped:
            await interaction.response.send_message("You don't have an active quest to skip!", ephemeral=True)
            return

        embed = discord.Embed(
            title="⏭️ Quest Skipped",
            description="Quest skipped! Run `/quest` again and I'll hand you a new one.",
            color=discord.Color.greyple()
        )
        self.stop()
        await interaction.response.edit_message(embed=embed, view=None)


class ClaimRewardView(discord.ui.View):
    def __init__(self, user_id: int, quest_config: dict):
        super().__init__(timeout=120)
        self.user_id = user_id
        self.quest_config = quest_config

    @discord.ui.button(label="Claim Reward", style=discord.ButtonStyle.success, emoji="🎁")
    async def claim_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your quest!", ephemeral=True)
            return

        with Session() as session:
            granted, quest = claim_quest_rewards(session, self.user_id)
            session.commit()

        if granted is None:
            await interaction.response.send_message("No rewards to claim!", ephemeral=True)
            return

        embed = create_quest_complete_embed(self.quest_config, granted)
        self.stop()
        await interaction.response.edit_message(embed=embed, view=None)


class NewQuestView(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=120)
        self.user_id = user_id

    @discord.ui.button(label="Get New Quest", style=discord.ButtonStyle.primary, emoji="\U0001f4dc")
    async def new_quest_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your quest!", ephemeral=True)
            return

        with Session() as session:
            user_quest = create_quest(session, self.user_id, hardcreate=True)
            quest_config = get_quest_by_id(user_quest.quest_id)

            quest_data = {
                "name": quest_config["name"],
                "description": quest_config["description"],
                "reward": quest_config["reward"],
            }
            progress_data = {
                "current": user_quest.progress,
                "total": user_quest.target,
            }
            expires_at = user_quest.expires_at
            session.commit()

        embed = create_quest_embed(quest_data, progress_data, expires_at=expires_at)
        view = SkipQuestView(user_id=self.user_id)
        self.stop()
        await interaction.response.edit_message(embed=embed, view=view)


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

    @commands.command()
    async def play(self, ctx):
        guess = Guess()
        await guess.play_game(ctx, self.bot, self.guess_sessions)

    @commands.slash_command(name="quest", description="View your current quest")
    async def quest(self, ctx):
        await ctx.defer()

        with Session() as session:
            user_quest = get_or_create_quest(session, ctx.author.id)

            now = datetime.utcnow()
            quest_config = get_quest_by_id(user_quest.quest_id)

            quest_data = {
                "name": quest_config["name"],
                "description": quest_config["description"],
                "reward": quest_config["reward"],
            }

            progress_data = {
                "current": user_quest.progress,
                "total": user_quest.target,
            }

            is_completed = user_quest.completed and not user_quest.rewards_claimed
            is_claimed = user_quest.completed and user_quest.rewards_claimed
            is_expired = not user_quest.completed and user_quest.expires_at <= now
            expires_at = user_quest.expires_at

            session.commit()

        if is_claimed:
            # Already claimed — just give a new quest directly
            with Session() as session:
                user_quest = create_quest(session, ctx.author.id, hardcreate=True)
                qc = get_quest_by_id(user_quest.quest_id)
                quest_data = {"name": qc["name"], "description": qc["description"], "reward": qc["reward"]}
                progress_data = {"current": user_quest.progress, "total": user_quest.target}
                expires_at = user_quest.expires_at
                session.commit()
            embed = create_quest_embed(quest_data, progress_data, expires_at=expires_at)
            view = SkipQuestView(user_id=ctx.author.id)

        elif is_expired:
            # Show expired quest with progress and a button to get a new one
            ts = int(expires_at.timestamp())
            embed = create_quest_embed(quest_data, progress_data)
            embed.color = discord.Color.dark_grey()
            embed.title = f"\u23f3 {quest_data['name']} \u2014 Expired"
            embed.add_field(
                name="Expired",
                value=f"This quest expired <t:{ts}:R>",
                inline=False
            )
            view = NewQuestView(user_id=ctx.author.id)

        elif is_completed:
            embed = create_quest_embed(quest_data, progress_data)
            embed.color = discord.Color.green()
            embed.title = f"\U0001f389 {quest_data['name']} \u2014 Complete!"
            embed.set_footer(text="Click below to claim your rewards!")
            view = ClaimRewardView(user_id=ctx.author.id, quest_config=quest_data)

        else:
            embed = create_quest_embed(quest_data, progress_data, expires_at=expires_at)
            view = SkipQuestView(user_id=ctx.author.id)

        await ctx.respond(embed=embed, view=view)


def setup(bot):
    """Setup the Cog"""
    bot.add_cog(Games(bot))