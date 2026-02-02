import random

from utils.global_sessions_registry import sessions
from utils.emotes import GOLD_EMOJI
from utils.custom_errors import NotEnoughItemError

from services.alchemy_services import use_potion



class UsableItemHandler:
    handlers = {}

    @classmethod
    def register(cls, name):
        """Decorator to register usable item handlers."""
        def decorator(func):
            cls.handlers[name.lower()] = func
            return func
        return decorator

    @classmethod
    def get_handler(cls, name):
        return cls.handlers.get(name.lower())


@UsableItemHandler.register("Potion of EXP")
def use_potion_of_exp(user_id: int):
    from services.exp_services import add_exp
    add_exp(user_id, 500)
    return "You drank a Potion of EXP and gained 500 EXP!"

@UsableItemHandler.register("Jar of EXP")
def use_jar_of_exp(user_id: int):
    from services.exp_services import add_exp
    add_exp(user_id, 2000)
    return "You used a Jar of EXP and gained 2000 EXP!"

@UsableItemHandler.register("Bag of Gold")
def use_bag_of_gold(user_id: int):
    from services.economy_services import add_gold
    add_gold(user_id, 100)
    return f"You opened your Bag of Gold and found 100 {GOLD_EMOJI} :O \nUse it responsibly :>"

@UsableItemHandler.register("Bread")
def use_bread(user_id: int):
    from services.jobs_services import JobsClass  # lazy import

    user = JobsClass(user_id)
    user.gain_energy(100)
    return "You ate the loaf of bread to gain some energy \n Energy +100"

@UsableItemHandler.register("Hint Key")
def use_hint_key(user_id: int):
    guess_sessions = sessions["guess"]

    if user_id in guess_sessions:
        guess_sessions[user_id].key_used = True
        return "🔑 You activated your Hint Key! Your next wrong guess will give a hint instead of ending the game.\n**Valid only for current stage**."

    return "You’re not currently playing a guessing game."

# =========================
# Potion Recipe Usables
# =========================

@UsableItemHandler.register("Potion Of Faster Recovery I")
def use_potion_faster_recovery_1(user_id: int):
    return use_potion(user_id, "Potion Of Faster Recovery I")

@UsableItemHandler.register("Potion Of Faster Recovery II")
def use_potion_faster_recovery_2(user_id: int):
    return use_potion(user_id, "Potion Of Faster Recovery II")

@UsableItemHandler.register("Potion Of Faster Recovery III")
def use_potion_faster_recovery_3(user_id: int):
    from services.jobs_services import JobsClass  # lazy import

    user = JobsClass(user_id)
    gained = random.randint(150, 200)
    user.gain_energy(gained)
    return f"You drank a Potion Of Faster Recovery III and gained {gained} Energy!"

@UsableItemHandler.register("Potion Of Luck I")
def use_potion_luck_1(user_id: int):
    return use_potion(user_id, "Potion Of Luck I")

@UsableItemHandler.register("Potion Of Luck II")
def use_potion_luck_2(user_id: int):
    return use_potion(user_id, "Potion Of Luck II")

@UsableItemHandler.register("Potion Of Luck III")
def use_potion_luck_3(user_id: int):
    from services.inventory_services import take_item, give_item
    try:
        take_item(user_id, 178, 1)
    except NotEnoughItemError:
        return "You don't have an Iron Box to spray the potion upon."

    roll = random.random() < 0.60

    if roll:
        give_item(user_id, 179, 1)
        return "The potion succeeds. Your Iron Box turned into a Platinum Box."

    give_item(user_id, 177, 1)
    return "The potion fizzles... Your Iron Box turned into a Stone Box"


@UsableItemHandler.register("Potion Of Love I")
def use_potion_love_1(user_id: int):
    return "This Potion can't be used gift it to others to express love xd"


@UsableItemHandler.register("Potion Of Hatred I")
def use_potion_hatred_1(user_id: int):
    return "This Potion can't be used gift it to others to express hate xd"
