import random

SYLPH_NAMES = [
    "Starry", "Snowy", "Luna", "Nova", "Misty", "Twinkle", "Willow",
    "Cloudy", "Dewdrop", "Moonbeam", "Sparkle", "Aurora", "Pebble",
    "Frosty", "Sunny", "Breeze", "Petal", "Glow", "Nimbus",
    "Skydancer", "Feather", "Starlight", "Comet", "Drizzle",
    "Flurry", "Shimmer", "Whisper", "Raindrop", "Crystal",
    "Firefly", "Velvet", "Echo", "Dream", "Puff", "Glimmer",
    "Snowdrop", "Moonpetal", "Starwhisper", "Softcloud",
    "Glowtail", "Silvermist", "Goldenbreeze", "Tinyflare",
    "Sweetnova", "Bubble", "Dazzle", "Moonblink",
    "Blossom", "Cherry", "Snowflake", "Stardust", "Moonlight",
    "Sunbeam", "Glowdrop", "Mistypuff", "Cloudlet", "Skye",
    "River", "Raindancer", "Stormy", "Lightning", "Ember",
    "Ash", "Cinder", "Flamelet", "Golden", "Silver",
    "Pearl", "Opal", "Ruby", "Sapphire", "Amethyst",
    "Diamond", "Shiny", "Glowy", "Shady", "Dusky",
    "Dawn", "Dusk", "Midnight", "Noon", "Auriel",
    "Lumina", "Celeste", "Astra", "Cosmo", "Orbit",
    "Nebula", "Galaxy", "Starlet", "Moonlet", "Comettail",
    "Spark", "Fizz", "Bubbly", "Tiny", "Mini",
    "Sprout", "Leaf", "Fern", "Moss", "Clover",
    "Tulip", "Rosebud", "Lilac", "Ivy", "Violet",
    "Snowpuff", "Frostwhisper", "Iceblink", "Chill",
    "Breezlet", "Windy", "Gust", "Zephyr", "Whirl",
    "Drifty", "Floaty", "Hover", "Glide", "Skimmer",
    "Glowbug", "Starlight", "buggy", "Lightlet",
    "Dreamlet", "Wish", "Hope", "Charm", "Lucky",
    "Shimmerdrop", "Twilite", "Radiance", "Lullaby",
    "Whimsy", "Pixie", "Sprite", "Fable", "Myth",
    "Echolet", "Softy", "Fluff", "Cotton", "Marsh",
    "Sugar", "Honey", "Caramel", "Toffee", "Vanilla",
    "Cream", "Pudding", "Jelly", "Candy", "Gummy",
    "Miku", "Piku", "Glowy", "Shiney"
]


def create_sylph_name():
    """Return a random cute fantasy-style Sylph name."""
    return random.choice(SYLPH_NAMES)