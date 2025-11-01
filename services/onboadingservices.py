from utils.embeds.welcomeembed import create_welcome_embed
from services.response_services import create_response

def greet(user_name: str):
    greeting_msg = create_response("welcome",1)
    embed = create_welcome_embed(user_name, greeting_msg)
    return embed