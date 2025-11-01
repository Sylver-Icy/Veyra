import discord
import random
import threading

gif_urls = [
    "https://cdn.discordapp.com/attachments/1354667633336778896/1434144678252646517/blow-kiss-anime-blow-kiss.gif",
    "https://cdn.discordapp.com/attachments/1275870091002777643/1434145423899230320/anime-funny.gif",
    "https://cdn.discordapp.com/attachments/1275870091002777643/1434145478412468384/anime-thanks.gif",
    "https://cdn.discordapp.com/attachments/1275870091002777643/1434145479196938293/cat-dance.gif",
    "https://cdn.discordapp.com/attachments/1275870091002777643/1434145479578615978/euller-smith-oshi-no-ko.gif",
    "https://cdn.discordapp.com/attachments/1275870091002777643/1434145480526397602/yay-yeah.gif",
    "https://cdn.discordapp.com/attachments/1275870091002777643/1434145480861945957/youre-welcome-you-are-welcome.gif",
    "https://cdn.discordapp.com/attachments/1275870091002777643/1434147545172545618/sousou-no-frieren-frieren.gif",
    "https://cdn.discordapp.com/attachments/1275870091002777643/1434147545613078688/blowkiss-anime.gif",
    "https://cdn.discordapp.com/attachments/1275870091002777643/1434147545935773768/sono-bisque-doll-wa-koi-wo-suru-royalmale.gif",
    "https://cdn.discordapp.com/attachments/1275870091002777643/1434147546284167178/anime-anime-girl.gif",
    "https://cdn.discordapp.com/attachments/1275870091002777643/1434147546632159275/wink-anime.gif"
]

used_urls = []
lock = threading.Lock()

def create_welcome_embed(user_name: str, greeting_msg: str):
    emojis = ["🌟", "🎉", "✨", "🎈", "🔥"]
    greetings = [
        "Welcome aboard!",
        "Welcum",
        "Hii there!",
        "Nice to see you here!",
        "Thx for joining!",
        "Glad you made it!",
        "Heya!",
        "Hola!!!"
    ]
    chosen_emoji = random.choice(emojis)
    chosen_greeting = random.choice(greetings)

    with lock:
        if not gif_urls:
            fill_gifs()
        chosen_gif = random.choice(gif_urls)
        gif_urls.remove(chosen_gif)
        used_urls.append(chosen_gif)

    embed = discord.Embed(
        title=f"{chosen_emoji} {chosen_greeting} {user_name.capitalize()}!",
        description=greeting_msg,
        color=random.randint(0, 0xFFFFFF)
    )
    embed.set_footer(text="Veyra • Alpha Test Phase")
    embed.set_image(url=chosen_gif)
    return embed

def fill_gifs():
    for url in used_urls:
        gif_urls.append(url)
    used_urls.clear()