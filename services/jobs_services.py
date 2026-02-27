import random
import discord

from sqlalchemy import select, func

from database.sessionmaker import Session

from models.users_model import User
from models.inventory_model import Items

from services.economy_services import add_gold, check_wallet, remove_gold
from services.inventory_services import give_item
from services.users_services import is_user
from services.response_services import create_response
from services.notif_services import send_notification
from services.alchemy_services import get_active_user_effect, expire_user_effect


from utils.custom_errors import VeyraError


# Global in-memory robbery shield tracker
# {user_id: shield_until_timestamp}
robbery_shields = {}

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
                lvl = user.level
                energy = user.energy
                max_energy = 35 + (15*lvl)
                return f"{energy}/{max_energy}"
            return 0



    def knight(self, energy_cost = 55):
        """
        Perform the 'knight' job, consuming energy and awarding gold if successful.

        :param energy_cost: Energy cost to perform the job. Default is 80.
        :return: A message indicating the result of the job.
        """
        eligible = self.consume_energy(energy_cost)

        if eligible:
            earning = random.randint(40, 90)
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
            "gold": 27,
            "woodenbox": 35,
            "stonebox": 25,
            "ironbox": 10,
            "platinumbox": 3
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
            try:
                give_item(self.user_id, 176, 1, True)
            except VeyraError:
                return (
                    "You dug for hours and unearthed a Wooden Box, but your satchel was already bursting. "
                    "With nowhere to stash it, you had to leave it half-buried in the dirt."
                )
            response = create_response("digger", 2, reward="Wooden Box")
            return response

        if reward == "stonebox":
            try:
                give_item(self.user_id, 177, 1, True)
            except VeyraError:
                return (
                    "You struck stone and found a Stone Box, but your pack was stuffed to the brim. "
                    "You marked the spot with a pebble and walked away empty-handed."
                )
            response = create_response("digger", 2, reward="Stone Box")
            return response

        if reward == "ironbox":
            try:
                give_item(self.user_id, 178, 1, True)
            except VeyraError:
                return (
                    "You finally hauled up an Iron Box... then remembered your inventory has the storage capacity of a napkin. "
                    "No space left, so you had to abandon it."
                )
            response = create_response("digger", 2, reward="Iron Box")

            return response

        try:
            give_item(self.user_id, 179, 1, True)
        except VeyraError:
            return (
                "You uncovered a Platinum Box gleaming in the soil, but your satchel couldn't fit another pebble. "
                "You left it behind, cursing your lack of space all the way home."
            )
        response = create_response("digger", 2, reward="Platinum Box")
        return response



    def miner(self, energy_cost = 60):
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
            "coal": 27,
            "copperore": 30,
            "ironore": 21,
            "silverore": 12
        }

        reward = random.choices(
        population=list(reward_distribution.keys()),
        weights=list(reward_distribution.values()),
        k=1
    )[0]

        if reward == "gold":
            add_gold(self.user_id, 25)
            response = create_response("miner", 2, gold=25)
            return response

        bonus = random.random() < 0.93  # True 93% of time

        if bonus:
            ore_amount = random.randint(3, 6)
        else:
            ore_amount = random.randint(12, 20)

        if reward == "coal":
            try:
                give_item(self.user_id, 187, ore_amount)
            except VeyraError:
                return (
                    f"You mined {ore_amount}x Coal, but your satchel had no room left. "
                    "With a heavy sigh, you left the haul by the tunnel mouth for someone luckier."
                )
            response = create_response("miner", 1, amount=ore_amount, ores="Coal")
            return response

        if reward == "copperore":
            try:
                give_item(self.user_id, 184, ore_amount)
            except VeyraError:
                return (
                    f"You pried loose {ore_amount}x Copper Ore, but your pack was packed tighter than a tavern on payday. "
                    "You stashed the ore behind a rock and left with empty hands."
                )
            response = create_response("miner", 1, amount=ore_amount, ores="Copper Ore")

            return response

        if reward == "ironore":
            try:
                give_item(self.user_id, 185, ore_amount)
            except VeyraError:
                return (
                    f"You dragged out {ore_amount}x Iron Ore, but your inventory was already full. "
                    "You had to leave the ore behind before the tunnel collapsed."
                )
            response = create_response("miner", 1, amount=ore_amount, ores="Iron Ore")

            return response

        try:
            give_item(self.user_id, 186, ore_amount)
        except VeyraError:
            return (
                f"You uncovered {ore_amount}x Silver Ore, but your satchel couldn't carry another shard. "
                "You reluctantly left the glittering prize in the darkness."
            )
        response = create_response("miner", 1, amount=ore_amount, ores="Silver Ore")

        return response


    def thief(self, target: discord.Member, energy_cost=65):
        """Attempt to steal gold from another user."""

        target_id = target.id

        if target_id == 1355171756624580772:
            return "I hire you idiot."

        if not is_user(target_id):
            return "They are not resident of Natlade"

        if target_id == self.user_id:
            return "Why do you wanna waste energy? try go robbing someone else"

        import time
        shield_until = robbery_shields.get(target_id)
        current_time = time.time()

        if shield_until and current_time < shield_until:
            remaining = int(shield_until - current_time)

            hours = remaining // 3600
            minutes = (remaining % 3600) // 60

            return (
                f"This person was recently robbed. Their house has security for another "
                f"{hours}h {minutes}m. Not the best time to try."
            )

        if not self.consume_energy(energy_cost):
            response = create_response("tired", 1)
            return response

        target_wealth = check_wallet(target_id)

        if target_wealth < 100:
            return f"@<{target_id}> was broke. You wasted your effort for nothing."

        # Check luck effect
        effect = get_active_user_effect(Session(), self.user_id)

        # Base success chance and cap
        success_chance = 0.5
        max_steal_cap = 300

        # Gamblers Fate effect
        if effect == "GAMBLERS FATE":
            success_chance = 0.9
            max_steal_cap = 500

        if random.random() > success_chance:
            # Failed robbery -> lose 30G fine
            remove_gold(self.user_id, 30)
            response = create_response("thief", 2, target=target_id, gold=0)
            return response

        # Calculate steal amount (5-10% capped at max_steal_cap)
        steal_percent = random.uniform(0.05, 0.10)
        stolen = int(min(target_wealth * steal_percent, max_steal_cap))

        # Victim loses 1% of wealth (no cap)
        victim_loss = int(target_wealth * 0.01)

        if stolen <= 0:
            return f"@<{target_id}> was too broke to steal anything meaningful."

        add_gold(self.user_id, stolen)
        remove_gold(target_id, victim_loss)

        # Apply 6 hour shield
        robbery_shields[target_id] = current_time + (6 * 60 * 60)

        response = create_response("thief", 1, target=target_id, gold=stolen)

        return response

    def explorer(self, energy_cost=20):
        "Explore around and find random item"
        if not self.consume_energy(energy_cost):
            response = create_response("tired", 1)
            return response

        rarity = random.choices(["Rare", "Common"], weights=[85, 15], k=1)[0]

        with Session() as session:
            item = (
                session.execute(
                    select(Items)
                    .where(Items.item_rarity == rarity)
                    .order_by(func.random())
                    .limit(1)
                )
                .scalars()
                .first()
            )

        try:
            give_item(self.user_id, item.item_id, 1)

        except VeyraError:
            return (
                f"You found {item.item_name} but your satchel was already stuffed to the brim. With no room to carry it, you left the find behind in the wilds."
            )

        return f"You explored and found something! ({item.item_name})"

async def regen_energy_for_all(bot):
    with Session() as session:
        # Fetch only users who are NOT already at max energy
        rows = session.execute(
            select(User.user_id, User.energy, User.level)
            .where(User.energy < (35 + (15 * User.level)))
        ).all()

        for user_id, energy, level in rows:
            max_energy = 35 + (15 * level)
            # Check active energy regen effect
            effect = get_active_user_effect(session, user_id)

            regen_amount = 1

            if effect == "ENERGY REGEN ELITE":
                regen_amount = 2
            elif effect == "ENERGY REGEN DEMON":
                regen_amount = 5

            new_energy = min(energy + regen_amount, max_energy)

            # Update energy
            session.execute(
                User.__table__.update()
                .where(User.user_id == user_id)
                .values(energy=new_energy)
            )

            # Fire notification ONLY if just reached max
            if energy < max_energy and new_energy == max_energy:
                await send_notification(bot, user_id, "ENERGY_FULL", session)

        session.commit()


async def notify_users_with_capped_or_overflow_energy(bot):
    """
    Loops through all users whose energy is at or above their maximum
    and sends them an ENERGY_FULL notification.
    """
    with Session() as session:
        rows = session.execute(
            select(User.user_id, User.energy, User.level)
            .where(User.energy >= (35 + (15 * User.level)))
        ).all()

        for user_id, energy, level in rows:
            await send_notification(bot, user_id, "ENERGY_FULL", session)