import random
from services.inventory_services import give_item
from database.sessionmaker import Session
from models.users_model import Daily


import asyncio
from services.response_services import create_response

class Guess:
    """
    Handles the core logic for the number guessing game, including picking number ranges,
    generating guesses, distributing rewards based on stages, and tracking daily game status.
    """
    def __init__(self):
        self.key_used = False

    @staticmethod
    def pick_number_range(stage):
        """
        Selects a random starting integer and returns a tuple representing the inclusive range
        for the guessing game based on the stage.

        Parameters:
            stage (int): The current stage of the game.

        Returns:
            tuple: A (low, high) tuple representing the range.
        """
        initial_int = random.randint(0, 100)
        if stage == 1:
            return (initial_int, initial_int + 1)
        elif stage == 2:
            return (initial_int, initial_int + 3)
        elif stage == 3:
            return (initial_int, initial_int + 9)
        else:
            return (initial_int, initial_int + 14)

    @staticmethod
    def guess_number(low, high):
        """
        Generates a random guess within the specified range.

        Parameters:
            low (int): Lower bound of the range (inclusive).
            high (int): Upper bound of the range (inclusive).

        Returns:
            int: A randomly selected number within the given range.
        """
        return random.randint(low, high)

    @staticmethod
    def calculate_and_distribute_reward(stage, user_id):
        """
        Distributes rewards to the user based on the stage achieved in the game.

        Parameters:
            stage (int): The current stage of the game.
            user_id (int): The unique identifier of the user.

        Returns:
            str: A description of the reward(s) given.
        """
        if stage == 1:
            give_item(user_id, 176, 1)
            return "1X Wooden Box"
        elif stage == 2:
            give_item(user_id, 177, 1)
            return "1X Stone Box"
        elif stage == 3:
            give_item(user_id, 177, 3)
            return "3X Stone Box"
        elif stage == 4:
            give_item(user_id, 178, 1)
            give_item(user_id, 176, 1)
            return "1X Iron Box and 1X Wooden Box"
        else:
            give_item(user_id, 179, 1)
            give_item(user_id, 177, 1)
            return "1X Platinum Box and 1X Stone Box"

    @staticmethod
    def fetch_or_create_daily(user_id: int):
        """
        Retrieves the Daily record for the user or creates one if it does not exist.

        Parameters:
            user_id (int): The unique identifier of the user.

        Returns:
            bool: The current status of the 'number_game' field for the user.
        """
        with Session() as session:
            daily = session.get(Daily, user_id)
            if not daily:
                new_entry = Daily(
                    user_id=user_id,
                    number_game=False
                )
                session.add(new_entry)
                session.commit()
                return False
            return daily.number_game


    async def play_game(self, ctx, bot, sessions):
        """
        Runs the full logic of the guessing game, including session check, daily check,
        handling user guesses, generating responses, calculating rewards, and sending messages.
        """
        # Check for active session
        if ctx.author.id in sessions:
            await ctx.send("⚠️ You already have an active Guess game running! Finish that one first.")
            return

        # Check daily limit
        already_played = Guess.fetch_or_create_daily(ctx.author.id)
        if already_played:
            response = create_response("played_today",1)
            await ctx.send(response)
            return

        sessions[ctx.author.id] = self
        try:
            loss_round = 5
            stage = 1
            while stage <= 4:
                low, high = Guess.pick_number_range(stage)
                correct = Guess.guess_number(low, high)
                response = create_response("win", stage, low=low, high=high)
                await ctx.send(response)

                stage_complete = False  # flag to track if player clears the stage

                while True:
                    try:
                        msg = await bot.wait_for(
                            "message",
                            check=lambda m: m.author == ctx.author and m.channel == ctx.channel,
                            timeout=30
                        )
                        guess = int(msg.content)
                    except ValueError:
                        continue

                    if guess != correct:
                        if self.key_used:
                            await ctx.send("🔑 Your Hint Key activates!")
                            await ctx.send("Hint: Try higher!" if guess < correct else "Hint: Try lower!")
                            self.key_used = False
                            # retry same stage without progressing
                            continue

                        # no key active or already used — lose
                        loss_round = stage
                        if stage == 1:
                            response = create_response("loose", 1, guess=guess, number=correct)
                        elif stage == 4:
                            response = create_response("loose", 4, guess=guess, number=correct)
                        elif abs(guess - correct) <= 3:
                            response = create_response("loose", 3, guess=guess, number=correct)
                        else:
                            response = create_response("loose", 2, guess=guess, number=correct)
                        await ctx.send(response)
                        stage = 5  # end game
                        break

                    else:
                        # correct guess — stage cleared
                        stage_complete = True
                        if self.key_used:
                            await ctx.send("🔑 Key effect wore off! 🗝️")
                            self.key_used = False
                        break

                if not stage_complete:
                    break  # end outer loop if player loses
                stage += 1

            reward = Guess.calculate_and_distribute_reward(loss_round, ctx.author.id)
            await ctx.send(f"Well and with that, game over. You get:\n{reward}")

            # Mark as played for today
            with Session() as session:
                daily = session.get(Daily, ctx.author.id)
                if daily:
                    daily.number_game = True
                    session.commit()
        except asyncio.TimeoutError:
            await ctx.send("I'm not gonna be waiting forever for your guess. Arghhh")
        finally:
            sessions.pop(ctx.author.id, None)


def reset_all_daily():
        """
        Resets the 'number_game' field to False for all users.
        Intended to be used for daily reset of the guessing game limit.
        """
        with Session() as session:
            all_dailies = session.query(Daily).all()
            for daily in all_dailies:
                daily.number_game = False
            session.commit()