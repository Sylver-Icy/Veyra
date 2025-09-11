from utils.custom_errors import VeyraError
from responses.responses_loader import RESPONSES
import json,random,os

def create_response(response_cataegory: str, response_mood: int, **kwargs) -> str:
    """Creates a response for each category based on mood"""
    data = RESPONSES[response_cataegory] [str(response_mood)]

    part1 = random.choice(data.get("part1", [""]))
    part2 = random.choice(data.get("part2", [""]))
    part3 = random.choice(data.get("part3", [""]))
    emoji = random.choice(data.get("emoji",[""]))

    response = f"{part1} {part2} {part3} {emoji}"
    try:
        response = response.format(**kwargs)
        #WORK FOR LATER T-T fix the custom erros and logging dude
    except KeyError:
        response ="smtng went wrong"

    return response
