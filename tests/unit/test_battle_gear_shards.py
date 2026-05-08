from database.seed_data import ITEMS
from domain.battle.gear_shards import (
    GEAR_SHARDS,
    GEAR_TYPE_SPELL,
    GEAR_TYPE_WEAPON,
    account_bound_shard_item_ids,
    droppable_shard_item_ids,
    get_shard_by_item_id,
    non_droppable_shard_item_ids,
)
from services.battle.content_registry import CONTENT_REGISTRY


def test_every_registered_weapon_and_spell_has_shard_metadata():
    shard_keys = {(shard.gear_type, shard.gear_key) for shard in GEAR_SHARDS}

    assert {
        (GEAR_TYPE_WEAPON, weapon_key)
        for weapon_key in CONTENT_REGISTRY.list_weapons()
    }.issubset(shard_keys)
    assert {
        (GEAR_TYPE_SPELL, spell_key)
        for spell_key in CONTENT_REGISTRY.list_spells()
    }.issubset(shard_keys)


def test_every_shard_has_seeded_item_row_and_unique_id():
    item_ids = [item["item_id"] for item in ITEMS]
    seeded_ids = set(item_ids)

    assert len(item_ids) == len(seeded_ids)
    for shard in GEAR_SHARDS:
        row = next(item for item in ITEMS if item["item_id"] == shard.item_id)
        assert row["item_type"] == "shard"
        assert row["item_rarity"] == shard.rarity


def test_weapon_shard_items_use_weapon_names_and_lore_descriptions():
    rows_by_id = {item["item_id"]: item for item in ITEMS}

    assert rows_by_id[3001]["item_name"] == "Training Blade"
    assert rows_by_id[3001]["item_description"] == (
        "Forged by an ancient mage, this blade grows sharper for those stubborn enough to keep swinging."
    )
    assert rows_by_id[3001]["item_icon"] == (
        "https://media.discordapp.net/attachments/1275870091002777643/1502169036564332714/image.png?ex=69febb6f&is=69fd69ef&hm=1ade0d41be5cc90ba83a7873ddeffb2db4c863f43259c6a00280d1904ce48e4e&=&format=webp&quality=lossless&width=1881&height=1881"
    )
    assert rows_by_id[3002]["item_name"] == "Dark Blade"
    assert rows_by_id[3002]["item_icon"] == (
        "https://media.discordapp.net/attachments/1275870091002777643/1502165405114826762/image.png?ex=69feb80d&is=69fd668d&hm=041b1863f5bc513749412961a41f0836c53ff69ee295524bc062da4d85e6ef19&=&format=webp&quality=lossless&width=1881&height=1881"
    )
    assert rows_by_id[3002]["item_description"] == (
        "A blade leaking dark energy, pulling in even the light around it and draining life from anything it touches."
    )
    assert rows_by_id[3003]["item_name"] == "Moon Slasher"
    assert rows_by_id[3003]["item_description"] == (
        "A sword from another world that fell to ours in a meteorite. It is strangely cold and elegant, and one look tells you it does not belong here."
    )
    assert rows_by_id[3003]["item_icon"] == (
        "https://media.discordapp.net/attachments/1275870091002777643/1502169591680471081/image.png?ex=69febbf3&is=69fd6a73&hm=4e6a8e670fba0fcc24bf730768c7ecaeb8301b1ea1a7637d143a84f6c28c3a7d&=&format=webp&quality=lossless&width=1881&height=1881"
    )
    assert rows_by_id[3004]["item_name"] == "Eternal Tome"
    assert rows_by_id[3004]["item_description"] == (
        "A restless tome filled with words that change whenever death draws near."
    )
    assert rows_by_id[3004]["item_icon"] == (
        "https://media.discordapp.net/attachments/1275870091002777643/1502170073249615892/image.png?ex=69febc66&is=69fd6ae6&hm=b4e77379086df00a3b7d3959c030ad23987e726b11dfb89038810d706aa33b9a&=&format=webp&quality=lossless&width=1881&height=1881"
    )
    assert rows_by_id[3005]["item_name"] == "Elephant Hammer"
    assert rows_by_id[3005]["item_description"] == (
        "A hammer with the weight of a charging beast, made to crush fear into silence."
    )
    assert rows_by_id[3005]["item_icon"] == (
        "https://media.discordapp.net/attachments/1275870091002777643/1502170532680826970/image.png?ex=69febcd3&is=69fd6b53&hm=57082f83e6436f65d8600707b5e7c27019675c3cc8f8d28f3e6eaf64527f1d2a&=&format=webp&quality=lossless&width=1881&height=1881"
    )
    assert rows_by_id[3006]["item_name"] == "Veyra's Grimoire"
    assert rows_by_id[3006]["item_description"] == (
        "Veyra's own grimoire, filled with spells that demand a price before they obey. Rewarded only to those she acknowledges."
    )
    assert rows_by_id[3006]["item_icon"] == (
        "https://media.discordapp.net/attachments/1275870091002777643/1502170905223106740/image.png?ex=69febd2c&is=69fd6bac&hm=1eb2b2bf3ccab5638e30fdf1a28b224a9182f190e08d0ab31d7e7d32b7f575d1&=&format=webp&quality=lossless&width=1881&height=1881"
    )
    assert rows_by_id[3007]["item_name"] == "Bardok's Claymore"
    assert rows_by_id[3007]["item_description"] == (
        "Bardok's massive claymore, carrying the weight of every battle he survived."
    )
    assert rows_by_id[3007]["item_icon"] == (
        "https://cdn.discordapp.com/attachments/1275870091002777643/1502171197729931314/image.png?ex=69febd72&is=69fd6bf2&hm=973ba1823b9436ef2e3ed73b1f85dd67a83ae459d516748b21306bec4d548f3c"
    )


def test_spell_shard_items_use_spell_names_and_lore_descriptions():
    rows_by_id = {item["item_id"]: item for item in ITEMS}

    assert rows_by_id[3008]["item_name"] == "Fireball"
    assert rows_by_id[3008]["item_description"] == (
        "A spell that concentrates mana into a giant ball of fire, built to burn enemies down before they get close."
    )
    assert rows_by_id[3008]["item_icon"] == (
        "https://media.discordapp.net/attachments/1275870091002777643/1502171528798666873/image.png?ex=69febdc1&is=69fd6c41&hm=5485baeb23084288110973eb71979160d90bc0ef886a4a2926f1c26a16c0d437&=&format=webp&quality=lossless&width=1881&height=1881"
    )
    assert rows_by_id[3009]["item_name"] == "Nightfall"
    assert rows_by_id[3009]["item_description"] == (
        "A spell that wraps the victim in creeping darkness, weakening them as time slips away."
    )
    assert rows_by_id[3009]["item_icon"] == (
        "https://media.discordapp.net/attachments/1275870091002777643/1502171752099217528/image.png?ex=69febdf6&is=69fd6c76&hm=d5c1e1a62f88083686da4f6133fe0e3e2d6306febbea97530be10213e23a0030&=&format=webp&quality=lossless&width=1881&height=1881"
    )
    assert rows_by_id[3010]["item_name"] == "Heavyshot"
    assert rows_by_id[3010]["item_description"] == (
        "Made by a poor rebel from an unknown village, this spell was born from anger at the inequality between rich and poor. It sets both fighters' HP equal."
    )
    assert rows_by_id[3010]["item_icon"] == (
        "https://media.discordapp.net/attachments/1275870091002777643/1502172035877437551/image.png?ex=69febe3a&is=69fd6cba&hm=27014936415ff0dbb7cdaec603411431513230f9f2349eafbdaa6cd3e8ff9b2f&=&format=webp&quality=lossless&width=1881&height=1881"
    )
    assert rows_by_id[3011]["item_name"] == "Erdtree Blessing"
    assert rows_by_id[3011]["item_description"] == (
        "A blessing of vitality that restores the caster's health little by little as the fight continues."
    )
    assert rows_by_id[3011]["item_icon"] == (
        "https://media.discordapp.net/attachments/1275870091002777643/1502172276131500132/image.png?ex=69febe73&is=69fd6cf3&hm=482f1cfb6e7d34d9850b8e063cdc64770e953e8af376d6766d5812e1741ad72a&=&format=webp&quality=lossless&width=1881&height=1881"
    )
    assert rows_by_id[3012]["item_name"] == "Frostbite"
    assert rows_by_id[3012]["item_description"] == (
        "The caster compresses mana into a focused burst of freezing magic, then throws it at the enemy to slow their movement and freeze their nerve."
    )
    assert rows_by_id[3012]["item_icon"] == (
        "https://cdn.discordapp.com/attachments/1275870091002777643/1502173069521719386/image.png?ex=69febf30&is=69fd6db0&hm=2e96f30b1130c55defe48f408cdb1aefcf51dec0d8ad9db80edb87b97ce4c417"
    )
    assert rows_by_id[3013]["item_name"] == "Veil of Darkness"
    assert rows_by_id[3013]["item_description"] == (
        "The caster pulls darkness into a heavy veil, blurring the enemy's aim and weakening clean hits."
    )
    assert rows_by_id[3013]["item_icon"] == (
        "https://media.discordapp.net/attachments/1275870091002777643/1502173440084410449/image.png?ex=69febf89&is=69fd6e09&hm=2dcc377fa962eff400a8bcab99aad34d02a7107e60a657247d86832262a7296c&=&format=webp&quality=lossless&width=525&height=525"
    )
    assert rows_by_id[3014]["item_name"] == "Earthquake"
    assert rows_by_id[3014]["item_description"] == (
        "A brutal spell that turns the ground against the enemy, knocking them off balance and breaking their defense open."
    )
    assert rows_by_id[3014]["item_icon"] == (
        "https://media.discordapp.net/attachments/1275870091002777643/1502174260607848489/image.png?ex=69fec04c&is=69fd6ecc&hm=01a3d76d51eac054f0de5d499d4ab8a91ceb3a2a6c3cdf9aa94b6b55c5f9c9f6&=&format=webp&quality=lossless&width=1881&height=1881"
    )


def test_shard_ids_are_reserved_in_catalog_order():
    assert [shard.item_id for shard in GEAR_SHARDS] == list(range(3001, 3015))


def test_mythic_shards_are_account_bound_and_not_droppable():
    mythic_shards = [shard for shard in GEAR_SHARDS if shard.rarity == "Mythic"]

    assert {shard.item_id for shard in mythic_shards} == account_bound_shard_item_ids()
    assert all(shard.account_bound for shard in mythic_shards)
    assert all(not shard.drop_pool for shard in mythic_shards)
    assert account_bound_shard_item_ids().isdisjoint(droppable_shard_item_ids())


def test_boxes_can_drop_normal_shards_but_never_mythic_or_starter_shards():
    droppable_ids = droppable_shard_item_ids()
    blocked_ids = non_droppable_shard_item_ids()

    assert get_shard_by_item_id(3002).item_id in droppable_ids
    assert get_shard_by_item_id(3008).item_id in droppable_ids
    assert 3001 in blocked_ids
    assert 3006 in blocked_ids
    assert 3007 in blocked_ids
