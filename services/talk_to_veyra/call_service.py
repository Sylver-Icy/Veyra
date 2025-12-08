import random

from services.economy_services import check_wallet
from services.exp_services import current_exp
from services.jobs_services import JobsClass
from services.response_services import create_response
from utils.emotes import GOLD_EMOJI

def handle_check_wallet(user_id):
    gold = check_wallet(user_id)
    return create_response("check_wallet", 1, user=f"<@{user_id}>", gold=gold, emoji=GOLD_EMOJI)



def handle_check_exp(user_id):
    exp, level = current_exp(user_id)
    return create_response("check_exp", 1, user=f"<@{user_id}>", level=level, exp=exp)


def handle_check_energy(user_id):
    user = JobsClass(user_id)
    energy = user.check_energy()
    return f"You current have {energy} energy..."


def handle_check_inventory(user_id):
    return "Just use '!check inventory' and stop bothering me"


def handle_quest(user_id):
    return "`/quest` exists for a reason no?"


def handle_shop(user_id):
    return "The channel name says **talk-to-veyra** not *make veyra run commands* bruh use `/shop`"


def handle_start_race(user_id):
    return "Do it in #bot-playground with `/start_race`"


def handle_flip_coin(user_id):
    result = random.choice(["head", "tail"])
    return create_response("flipcoin", 1, result=result)




SERVICE_MAP = {
    "LABEL_0": handle_check_wallet,
    "LABEL_1": handle_check_exp,
    "LABEL_2": handle_check_energy,
    "LABEL_3": handle_check_inventory,
    "LABEL_4": handle_quest,
    "LABEL_5": handle_shop,
    "LABEL_6": handle_start_race,
    "LABEL_7": handle_flip_coin
}

def run_service(label: str, user_id: int):
    handler = SERVICE_MAP.get(label)

    if handler is None:
        return "The is no such command twin"

    return handler(user_id)