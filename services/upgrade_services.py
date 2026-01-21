from database.sessionmaker import Session

from models.users_model import Upgrades, UpgradeDefinitions

from services.economy_services import remove_gold, check_wallet



def upgrade_building(user_id: int, building_name: str):
    building_name = building_name.lower()
    if not  building_exist(building_name):
        return "There is no such building?? what you tryna upgrade."

    with Session() as session:
        user_upgrade = session.get(Upgrades, (user_id, building_name))

        if not user_upgrade:
            return f"You don't own the required building. BUY IT BEFORE TRYING TO UPGRADE. `!unlock <{building_name}>`"

        # fetch next level definition
        next_level = user_upgrade.level + 1

        upgrade_def = session.get(UpgradeDefinitions, (building_name, next_level))
        if not upgrade_def:
            return f"{building_name} is already at maximum level." #user already at max lvl

        gold = check_wallet(user_id)

        if gold < upgrade_def.cost:

            return (f"You are missing {upgrade_def.cost - gold} gold for the upgrade")

        remove_gold(user_id, upgrade_def.cost)

        user_upgrade.level = next_level
        session.commit()
        return f"Congratulations {building_name} has been upgraded to {next_level}"

def building_lvl(user_id: int, building_name: str):
    building_name = building_name.lower()
    if not building_exist(building_name):
        return "Incorrect name"

    with Session() as session:
        user = session.get(Upgrades, (user_id, building_name))
        if not user:
            return 0
        return user.level


def building_exist(building_name: str):
    building_name = building_name.lower()
    with Session() as session:
        building = session.get(UpgradeDefinitions, (building_name, 1))
        return bool(building)


def get_next_upgrade_info(user_id: int, building_name: str):
    building_name = building_name.lower()
    if not building_exist(building_name):
        return "Typo???"

    with Session() as session:
        current = session.get(Upgrades, (user_id, building_name))

        if not current:
            return f"You don’t even own {building_name} yet. And you are dreaming about upgrading it? Lol lol.\nBuy it first with `!unlock {building_name}`"

        next_def = session.get(UpgradeDefinitions, (building_name, current.level + 1))

        if not next_def:
            return f"{building_name} is already maxed out."

        return {
            "current_level": current.level,
            "cost": next_def.cost,
            "description": next_def.effect_description
        }

def buy_building(user_id: int, building_name: str):
    building_name = building_name.lower()
    if not building_exist(building_name):
        return "there is no such building which I'm aware of tbh"

    with Session() as session:
        existing = session.get(Upgrades, (user_id, building_name))
        if existing:
            return f"{building_name} has already been unlocked. You can upgrade it via `!upgrade <{building_name}>`"

        building_stats = session.get(UpgradeDefinitions, (building_name, 1))
        user_gold = check_wallet(user_id)
        building_cost = building_stats.cost

        #unlock inventory and pockets for free
        if building_cost == 0:
            new_building = Upgrades(user_id=user_id, upgrade_name=building_name, level=1)
            session.add(new_building)
            session.commit()
            return f"{building_name} has been unlocked. ;)"

        if user_gold < building_cost:
            return f"You need {building_cost} gold to buy a {building_name}. You currently have only {user_gold}.\nHow about try doing some `/quest` ??"

        remove_gold(user_id, building_cost)
        new_building = Upgrades(user_id=user_id, upgrade_name=building_name, level=1)
        session.add(new_building)
        session.commit()
        return f"{building_name} has been unlocked. ;)"