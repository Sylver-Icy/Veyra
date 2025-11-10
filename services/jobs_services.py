import random

from database.sessionmaker import Session

from models.users_model import User

from services.economy_services import add_gold


class Jobs:
    def __init__(self, user_id, user_name):
        self.user_id = user_id
        self.name = user_name

    def gain_energy(self, energy_gain = 1):

        with Session() as session:
            user = session.get(User, self.user_id)
            if user:
                max_energy = 10 + (10 * user.level)
                if user.energy < max_energy:
                    user.energy += energy_gain
                    session.commit()

    def consume_energy(self, energy_cost: int):

        with Session() as session:
            user = session.get(User, self.user_id)
            if user:
                if user.energy >= energy_cost:
                    user.energy -= energy_cost
                    session.commit()
                    return True

                return False
            return False

    def knight(self, energy_cost = 100):
        eligible = self.consume_energy(energy_cost)

        if eligible:
            earning = random.randint(30, 50)
            add_gold(self.user_id, earning)
            return (f"You earned {earning} gold")

        return "Too tired consider taking rest?"


    