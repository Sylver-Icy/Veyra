from utils.custom_errors import VeyraError
import json,random,os

RESPONSE_FILE = os.path.join(os.path.dirname(__file__), "..", "utils", "responses.json")

with open(RESPONSE_FILE, "r", encoding="utf-8") as f:
    RESPONSES = json.load(f)

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
        response ="something went wrong"

    return response

print(create_response("level_up",1,user="Sylver",level=20))
