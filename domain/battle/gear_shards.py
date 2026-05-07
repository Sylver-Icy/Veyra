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


GEAR_SHARDS = (
    GearShardDefinition(GEAR_TYPE_WEAPON, "trainingblade", 3001, "Training Blade Shard", "Common", False, False),
    GearShardDefinition(GEAR_TYPE_WEAPON, "darkblade", 3002, "Dark Blade Shard", "Legendary", False, True),
    GearShardDefinition(GEAR_TYPE_WEAPON, "moonslasher", 3003, "Moon Slasher Shard", "Epic", False, True),
    GearShardDefinition(GEAR_TYPE_WEAPON, "eternaltome", 3004, "Eternal Tome Shard", "Rare", False, True),
    GearShardDefinition(GEAR_TYPE_WEAPON, "elephanthammer", 3005, "Elephant Hammer Shard", "Common", False, True),
    GearShardDefinition(GEAR_TYPE_WEAPON, "veyrasgrimoire", 3006, "Veyra's Grimoire Shard", "Mythic", True, False),
    GearShardDefinition(GEAR_TYPE_WEAPON, "bardoksclaymore", 3007, "Bardok's Claymore Shard", "Mythic", True, False),
    GearShardDefinition(GEAR_TYPE_SPELL, "fireball", 3008, "Fireball Shard", "Rare", False, True),
    GearShardDefinition(GEAR_TYPE_SPELL, "nightfall", 3009, "Nightfall Shard", "Common", False, True),
    GearShardDefinition(GEAR_TYPE_SPELL, "heavyshot", 3010, "Heavyshot Shard", "Legendary", False, True),
    GearShardDefinition(GEAR_TYPE_SPELL, "erdtreeblessing", 3011, "Erdtree Blessing Shard", "Epic", False, True),
    GearShardDefinition(GEAR_TYPE_SPELL, "frostbite", 3012, "Frostbite Shard", "Epic", False, True),
    GearShardDefinition(GEAR_TYPE_SPELL, "veilofdarkness", 3013, "Veil of Darkness Shard", "Rare", False, True),
    GearShardDefinition(GEAR_TYPE_SPELL, "earthquake", 3014, "Earthquake Shard", "Rare", False, True),
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
            "item_description": f"Collect shards to unlock {shard.item_name.removesuffix(' Shard')}.",
            "item_type": "shard",
            "item_rarity": shard.rarity,
            "item_icon": None,
            "item_durability": None,
            "item_price": None,
            "item_usable": False,
        }
        for shard in GEAR_SHARDS
    ]
