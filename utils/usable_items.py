from services.exp_services import add_exp
from services.economy_services import add_gold

from utils.custom_errors import NotEnoughItemError
from utils.global_sessions_registry import sessions


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
    add_exp(user_id, 500)
    return "You drank a Potion of EXP and gained 500 EXP!"

@UsableItemHandler.register("Jar of EXP")
def use_jar_of_exp(user_id: int):
    add_exp(user_id, 2000)
    return "You used a Jar of EXP and gained 2000 EXP!"

@UsableItemHandler.register("Bag of Gold")
def use_bag_of_gold(user_id: int):
    add_gold(user_id, 100)
    return "You opened you Bag of Gold and found 100 gold :O \nUse it responsibly :>"

@UsableItemHandler.register("Hint Key")
def use_hint_key(user_id: int):
    guess_sessions = sessions["guess"]
    print("Current guess sessions:", guess_sessions)
    print("Session type for user:", type(guess_sessions.get(user_id)))
    if user_id in guess_sessions:
        guess_sessions[user_id].key_used = True
        return "🔑 You activated your Hint Key! Your next wrong guess will give a hint instead of ending the game.\n**Valid only for current stage**."


    return "You’re not currently playing a guessing game."