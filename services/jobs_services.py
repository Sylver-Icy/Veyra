import random
import discord


from database.sessionmaker import Session

from models.users_model import User

from services.economy_services import add_gold, check_wallet, remove_gold
from services.inventory_services import give_item
from services.users_services import is_user
from services.response_services import create_response


class JobsClass:
    def __init__(self, user_id):
        """
        Initialize a Jobs instance for a user.

        :param user_id: ID of the user.
        """
        self.user_id = user_id

    def gain_energy(self, energy_gain = 1):
        """
        Increase the user's energy by a specified amount, ignoring the maximum allowed energy.

        :param energy_gain: Amount of energy to gain. Default is 1.
        """
        with Session() as session:
            user = session.get(User, self.user_id)
            if user:
                    user.energy = user.energy + energy_gain
                    session.commit()

    def consume_energy(self, energy_cost: int):
        """
        Consume a specified amount of energy from the user if enough energy is available.

        :param energy_cost: The amount of energy to consume.
        :return: True if energy was successfully consumed, False otherwise.
        """
        with Session() as session:
            user = session.get(User, self.user_id)
            if user:
                if user.energy >= energy_cost:
                    user.energy -= energy_cost
                    session.commit()
                    return True

                return False
            return False

    def check_energy(self):
        """
        Check the current energy level of the user.

        :return: The user's current energy.
        """
        with Session() as session:
            user = session.get(User, self.user_id)
            if user:
                return user.energy
            return 0



    def knight(self, energy_cost = 80):
        """
        Perform the 'knight' job, consuming energy and awarding gold if successful.

        :param energy_cost: Energy cost to perform the job. Default is 80.
        :return: A message indicating the result of the job.
        """
        eligible = self.consume_energy(energy_cost)

        if eligible:
            earning = random.randint(30, 50)
            add_gold(self.user_id, earning)
            response = create_response("knight", 1, gold=earning)
            return response

        response = create_response("tired", 1)
        return response


    def digger(self, energy_cost = 70):
        """
        Perform the 'digger' job, consuming energy and awarding a random reward.

        :param energy_cost: Energy cost to perform the job. Default is 70.
        :return: A message indicating the reward received.
        """
        eligible = self.consume_energy(energy_cost)
        if not eligible:
            response = create_response("tired", 1)

            return response

        reward_distribution = {
            "gold": 29,
            "woodenbox": 40,
            "stonebox": 25,
            "ironbox": 5,
            "platinumbox": 1
        }

        reward = random.choices(
        population=list(reward_distribution.keys()),
        weights=list(reward_distribution.values()),
        k=1
    )[0]
        if reward == "gold":
            add_gold(self.user_id, 20)
            response = create_response("digger", 1, gold=20)
            return response

        if reward == "woodenbox":
            give_item(self.user_id, 176, 1)
            response = create_response("digger", 2, reward="Wooden Box")
            return response

        if reward == "stonebox":
            give_item(self.user_id, 177, 1)
            response = create_response("digger", 2, reward="Stone Box")
            return response

        if reward == "ironbox":
            give_item(self.user_id, 178, 1)
            response = create_response("digger", 2, reward="Iron Box")

            return response

        give_item(self.user_id, 179, 1)
        response = create_response("digger", 2, reward="Platinum Box")
        return response



    def miner(self, energy_cost = 90):
        """
        Perform the 'miner' job, consuming energy and awarding a random ore or gold reward.

        :param energy_cost: Energy cost to perform the job. Default is 50.
        :return: A message indicating the reward received.
        """
        eligible = self.consume_energy(energy_cost)
        if not eligible:
            response = create_response("tired", 1)
            return response


        reward_distribution = {
            "gold": 10,
            "coal": 30,
            "copperore": 30,
            "ironore": 20,
            "silverore": 10
        }

        reward = random.choices(
        population=list(reward_distribution.keys()),
        weights=list(reward_distribution.values()),
        k=1
    )[0]

        if reward == "gold":
            add_gold(self.user_id, 15)
            response = create_response("miner", 2, gold=15)
            return response

        ore_amount = random.randint(1, 3)
        if reward == "coal":
            give_item(self.user_id, 187, ore_amount)
            response = create_response("miner", 1, amount=ore_amount, ores="Coal")
            return response

        if reward == "copperore":
            give_item(self.user_id, 184, ore_amount)
            response = create_response("miner", 1, amount=ore_amount, ores="Copper Ore")

            return response

        if reward == "ironore":
            give_item(self.user_id, 185, ore_amount)
            response = create_response("miner", 1, amount=ore_amount, ores="Iron Ore")

            return response

        give_item(self.user_id, 186, ore_amount)
        response = create_response("miner", 1, amount=ore_amount, ores="Silver Ore")

        return response


    def thief(self, target: discord.Member, energy_cost=60):
        """Attempt to steal gold from another user."""

        target_id = target.id
        target_name = target.display_name

        if not is_user(target_id):
            return "They are not resident of Natlade"

        if target_id == 1355171756624580772:
            return "I hire you idiot."

        if target_id == self.user_id:
            return "Why do you wanna waste energy? try go robbing someone else"

        if not self.consume_energy(energy_cost):
            response = create_response("tired", 1)
            return response

        target_wealth = check_wallet(target_id)

        if target_wealth < 50:
            return f"{target_name} was broke. You wasted your effort for nothing."

        if random.randint(0, 1) == 0:
            remove_gold(self.user_id, 30)
            response = create_response("thief", 2, target=target_name, gold=0)
            return response

        stolen = int(min(target_wealth * 0.10, 150))
        fine = int(min(target_wealth * 0.01, 50))

        add_gold(self.user_id, stolen)
        remove_gold(target_id, fine)

        response = create_response("thief", 1, target=target_name, gold=stolen)

        return response


def regen_energy_for_all():
    """Give +1 energy to all users who aren't capped."""
    with Session() as session:
        users = session.query(User).all()
        for user in users:
            max_energy = 35 + (15 * user.level)
            if user.energy < max_energy:
                user.energy = min(user.energy + 1, max_energy)
        session.commit()