"""Battle gear shard catalog.

Shard inventory rows are the source of truth for gear ownership. One shard
unlocks the matching weapon or spell; levels can layer on this later.
"""

from dataclasses import dataclass


GEAR_TYPE_WEAPON = "weapon"
GEAR_TYPE_SPELL = "spell"
STARTER_WEAPON_KEY = "trainingblade"
CAMPAIGN_GEAR_REWARD_WEAPONS = {
    10: "veyrasgrimoire",
    15: "bardoksclaymore",
}


@dataclass(frozen=True)
class GearShardDefinition:
    gear_type: str
    gear_key: str
    item_id: int
    item_name: str
    rarity: str
    account_bound: bool
    drop_pool: bool
    item_description: str | None = None
    item_icon: str | None = None


GEAR_SHARDS = (
    GearShardDefinition(
        GEAR_TYPE_WEAPON,
        "trainingblade",
        3001,
        "Training Blade",
        "Common",
        False,
        False,
        "Forged by an ancient mage, this blade grows sharper for those stubborn enough to keep swinging.",
        "https://media.discordapp.net/attachments/1275870091002777643/1502169036564332714/image.png?ex=69febb6f&is=69fd69ef&hm=1ade0d41be5cc90ba83a7873ddeffb2db4c863f43259c6a00280d1904ce48e4e&=&format=webp&quality=lossless&width=1881&height=1881",
    ),
    GearShardDefinition(
        GEAR_TYPE_WEAPON,
        "darkblade",
        3002,
        "Dark Blade",
        "Legendary",
        False,
        True,
        "A blade leaking dark energy, pulling in even the light around it and draining life from anything it touches.",
        "https://media.discordapp.net/attachments/1275870091002777643/1502165405114826762/image.png?ex=69feb80d&is=69fd668d&hm=041b1863f5bc513749412961a41f0836c53ff69ee295524bc062da4d85e6ef19&=&format=webp&quality=lossless&width=1881&height=1881",
    ),
    GearShardDefinition(
        GEAR_TYPE_WEAPON,
        "moonslasher",
        3003,
        "Moon Slasher",
        "Epic",
        False,
        True,
        "A sword from another world that fell to ours in a meteorite. It is strangely cold and elegant, and one look tells you it does not belong here.",
        "https://media.discordapp.net/attachments/1275870091002777643/1502169591680471081/image.png?ex=69febbf3&is=69fd6a73&hm=4e6a8e670fba0fcc24bf730768c7ecaeb8301b1ea1a7637d143a84f6c28c3a7d&=&format=webp&quality=lossless&width=1881&height=1881",
    ),
    GearShardDefinition(
        GEAR_TYPE_WEAPON,
        "eternaltome",
        3004,
        "Eternal Tome",
        "Rare",
        False,
        True,
        "A restless tome filled with words that change whenever death draws near.",
        "https://media.discordapp.net/attachments/1275870091002777643/1502170073249615892/image.png?ex=69febc66&is=69fd6ae6&hm=b4e77379086df00a3b7d3959c030ad23987e726b11dfb89038810d706aa33b9a&=&format=webp&quality=lossless&width=1881&height=1881",
    ),
    GearShardDefinition(
        GEAR_TYPE_WEAPON,
        "elephanthammer",
        3005,
        "Elephant Hammer",
        "Common",
        False,
        True,
        "A hammer with the weight of a charging beast, made to crush fear into silence.",
        "https://media.discordapp.net/attachments/1275870091002777643/1502170532680826970/image.png?ex=69febcd3&is=69fd6b53&hm=57082f83e6436f65d8600707b5e7c27019675c3cc8f8d28f3e6eaf64527f1d2a&=&format=webp&quality=lossless&width=1881&height=1881",
    ),
    GearShardDefinition(
        GEAR_TYPE_WEAPON,
        "veyrasgrimoire",
        3006,
        "Veyra's Grimoire",
        "Mythic",
        True,
        False,
        "Veyra's own grimoire, filled with spells that demand a price before they obey. Rewarded only to those she acknowledges.",
        "https://media.discordapp.net/attachments/1275870091002777643/1502170905223106740/image.png?ex=69febd2c&is=69fd6bac&hm=1eb2b2bf3ccab5638e30fdf1a28b224a9182f190e08d0ab31d7e7d32b7f575d1&=&format=webp&quality=lossless&width=1881&height=1881",
    ),
    GearShardDefinition(
        GEAR_TYPE_WEAPON,
        "bardoksclaymore",
        3007,
        "Bardok's Claymore",
        "Mythic",
        True,
        False,
        "Bardok's massive claymore, carrying the weight of every battle he survived.",
        "https://cdn.discordapp.com/attachments/1275870091002777643/1502171197729931314/image.png?ex=69febd72&is=69fd6bf2&hm=973ba1823b9436ef2e3ed73b1f85dd67a83ae459d516748b21306bec4d548f3c",
    ),
    GearShardDefinition(
        GEAR_TYPE_SPELL,
        "fireball",
        3008,
        "Fireball",
        "Rare",
        False,
        True,
        "A spell that concentrates mana into a giant ball of fire, built to burn enemies down before they get close.",
        "https://media.discordapp.net/attachments/1275870091002777643/1502171528798666873/image.png?ex=69febdc1&is=69fd6c41&hm=5485baeb23084288110973eb71979160d90bc0ef886a4a2926f1c26a16c0d437&=&format=webp&quality=lossless&width=1881&height=1881",
    ),
    GearShardDefinition(
        GEAR_TYPE_SPELL,
        "nightfall",
        3009,
        "Nightfall",
        "Common",
        False,
        True,
        "A spell that wraps the victim in creeping darkness, weakening them as time slips away.",
        "https://media.discordapp.net/attachments/1275870091002777643/1502171752099217528/image.png?ex=69febdf6&is=69fd6c76&hm=d5c1e1a62f88083686da4f6133fe0e3e2d6306febbea97530be10213e23a0030&=&format=webp&quality=lossless&width=1881&height=1881",
    ),
    GearShardDefinition(
        GEAR_TYPE_SPELL,
        "heavyshot",
        3010,
        "Heavyshot",
        "Legendary",
        False,
        True,
        "Made by a poor rebel from an unknown village, this spell was born from anger at the inequality between rich and poor. It sets both fighters' HP equal.",
        "https://media.discordapp.net/attachments/1275870091002777643/1502172035877437551/image.png?ex=69febe3a&is=69fd6cba&hm=27014936415ff0dbb7cdaec603411431513230f9f2349eafbdaa6cd3e8ff9b2f&=&format=webp&quality=lossless&width=1881&height=1881",
    ),
    GearShardDefinition(
        GEAR_TYPE_SPELL,
        "erdtreeblessing",
        3011,
        "Erdtree Blessing",
        "Epic",
        False,
        True,
        "A blessing of vitality that restores the caster's health little by little as the fight continues.",
        "https://media.discordapp.net/attachments/1275870091002777643/1502172276131500132/image.png?ex=69febe73&is=69fd6cf3&hm=482f1cfb6e7d34d9850b8e063cdc64770e953e8af376d6766d5812e1741ad72a&=&format=webp&quality=lossless&width=1881&height=1881",
    ),
    GearShardDefinition(
        GEAR_TYPE_SPELL,
        "frostbite",
        3012,
        "Frostbite",
        "Epic",
        False,
        True,
        "The caster compresses mana into a focused burst of freezing magic, then throws it at the enemy to slow their movement and freeze their nerve.",
        "https://cdn.discordapp.com/attachments/1275870091002777643/1502173069521719386/image.png?ex=69febf30&is=69fd6db0&hm=2e96f30b1130c55defe48f408cdb1aefcf51dec0d8ad9db80edb87b97ce4c417",
    ),
    GearShardDefinition(
        GEAR_TYPE_SPELL,
        "veilofdarkness",
        3013,
        "Veil of Darkness",
        "Rare",
        False,
        True,
        "The caster pulls darkness into a heavy veil, blurring the enemy's aim and weakening clean hits.",
        "https://media.discordapp.net/attachments/1275870091002777643/1502173440084410449/image.png?ex=69febf89&is=69fd6e09&hm=2dcc377fa962eff400a8bcab99aad34d02a7107e60a657247d86832262a7296c&=&format=webp&quality=lossless&width=525&height=525",
    ),
    GearShardDefinition(
        GEAR_TYPE_SPELL,
        "earthquake",
        3014,
        "Earthquake",
        "Rare",
        False,
        True,
        "A brutal spell that turns the ground against the enemy, knocking them off balance and breaking their defense open.",
        "https://media.discordapp.net/attachments/1275870091002777643/1502174260607848489/image.png?ex=69fec04c&is=69fd6ecc&hm=01a3d76d51eac054f0de5d499d4ab8a91ceb3a2a6c3cdf9aa94b6b55c5f9c9f6&=&format=webp&quality=lossless&width=1881&height=1881",
    ),
)

_BY_GEAR = {(shard.gear_type, shard.gear_key): shard for shard in GEAR_SHARDS}
_BY_ITEM_ID = {shard.item_id: shard for shard in GEAR_SHARDS}


def get_gear_shard(gear_type: str, gear_key: str) -> GearShardDefinition | None:
    return _BY_GEAR.get((gear_type, gear_key))


def get_weapon_shard(weapon_key: str) -> GearShardDefinition | None:
    return get_gear_shard(GEAR_TYPE_WEAPON, weapon_key)


def get_spell_shard(spell_key: str) -> GearShardDefinition | None:
    return get_gear_shard(GEAR_TYPE_SPELL, spell_key)


def get_shard_by_item_id(item_id: int) -> GearShardDefinition | None:
    return _BY_ITEM_ID.get(item_id)


def starter_weapon_shard() -> GearShardDefinition:
    shard = get_weapon_shard(STARTER_WEAPON_KEY)
    if shard is None:
        raise RuntimeError("Starter weapon shard is not registered")
    return shard


def campaign_gear_reward_for_stage(stage: int) -> GearShardDefinition | None:
    weapon_key = CAMPAIGN_GEAR_REWARD_WEAPONS.get(stage)
    if weapon_key is None:
        return None
    return get_weapon_shard(weapon_key)


def shard_item_ids() -> set[int]:
    return set(_BY_ITEM_ID)


def droppable_shard_item_ids() -> set[int]:
    return {shard.item_id for shard in GEAR_SHARDS if shard.drop_pool and not shard.account_bound}


def non_droppable_shard_item_ids() -> set[int]:
    return shard_item_ids() - droppable_shard_item_ids()


def account_bound_shard_item_ids() -> set[int]:
    return {shard.item_id for shard in GEAR_SHARDS if shard.account_bound}


def is_shard_item(item_id: int) -> bool:
    return item_id in _BY_ITEM_ID


def is_account_bound_shard_item(item_id: int) -> bool:
    shard = get_shard_by_item_id(item_id)
    return bool(shard and shard.account_bound)


def shard_item_rows() -> list[dict]:
    return [
        {
            "item_id": shard.item_id,
            "item_name": shard.item_name,
            "item_description": shard.item_description or f"Collect shards to unlock {shard.item_name.removesuffix(' Shard')}.",
            "item_type": "shard",
            "item_rarity": shard.rarity,
            "item_icon": shard.item_icon,
            "item_durability": None,
            "item_price": None,
            "item_usable": False,
        }
        for shard in GEAR_SHARDS
    ]
