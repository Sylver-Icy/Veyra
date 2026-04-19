from services.battle.arena_class import FrozenArena, IrritationArena, LavaArena
from services.battle.battle_class import Battle
from services.battle.campaign.bardok_ai import BardokAI
from services.battle.spell_class import (
    Earthquake,
    ErdtreeBlessing,
    Fireball,
    FrostBite,
    Heavyshot,
    Nightfall,
    VeilOfDarkness,
)
from services.battle.weapon_class import (
    BardoksClaymore,
    DarkBlade,
    ElephantHammer,
    EternalTome,
    MoonSlasher,
    TrainingBlade,
    VeyrasGrimoire,
)


def make_battle(name="Tester", spell=None, weapon=None):
    return Battle(name, spell or Nightfall(), weapon or TrainingBlade())


def test_fireball_deals_damage_and_spends_mana():
    caster = make_battle("Mage", spell=Fireball())
    caster.mana = 20
    target = make_battle("Target")

    ok, _ = caster.cast(target)

    assert ok is True
    assert caster.mana == 5
    assert target.hp == 24


def test_nightfall_applies_status_to_target():
    caster = make_battle("Mage")
    target = make_battle("Target")

    ok, _ = caster.cast(target)

    assert ok is True
    assert target.status_effect["nightfall"]["duration"] == 5
    assert target.status_effect["nightfall"]["source"] is caster


def test_heavyshot_sets_target_hp_to_casters_hp():
    caster = make_battle("Mage", spell=Heavyshot())
    caster.mana = 20
    caster.hp = 31
    target = make_battle("Target")
    target.hp = 14

    ok, _ = caster.cast(target)

    assert ok is True
    assert target.hp == 31


def test_erdtree_blessing_applies_largeheal_on_caster():
    caster = make_battle("Mage", spell=ErdtreeBlessing())
    caster.mana = 20
    target = make_battle("Target")

    ok, _ = caster.cast(target)

    assert ok is True
    assert caster.status_effect["largeheal"]["duration"] == 4


def test_frostbite_adds_frost_and_reduces_speed():
    caster = make_battle("Mage", spell=FrostBite())
    target = make_battle("Target")
    original_speed = target.speed

    ok, _ = caster.cast(target)

    assert ok is True
    assert target.frost == 5
    assert target.speed == original_speed - 1


def test_veil_of_darkness_applies_status_to_caster():
    caster = make_battle("Mage", spell=VeilOfDarkness())
    caster.mana = 20
    target = make_battle("Target")

    ok, _ = caster.cast(target)

    assert ok is True
    assert caster.status_effect["veilofdarkness"]["duration"] == 4


def test_earthquake_breaks_defense_and_speed():
    caster = make_battle("Mage", spell=Earthquake())
    caster.mana = 20
    target = make_battle("Target")
    target.defense = 18
    target.speed = 15

    ok, _ = caster.cast(target)

    assert ok is True
    assert target.hp == 35
    assert target.defense == 0
    assert target.speed == 12


def test_training_blade_increases_attack_on_hit():
    attacker = make_battle("Attacker", weapon=TrainingBlade())
    defender = make_battle("Defender")

    result = attacker.weapon.on_attack_success(attacker, defender, 10)

    assert attacker.attack == 11
    assert "attack increased by 1" in result


def test_moon_slasher_adds_frost_on_hit():
    attacker = make_battle("Attacker", weapon=MoonSlasher())
    defender = make_battle("Defender")

    attacker.weapon.on_attack_success(attacker, defender, 10)

    assert defender.frost == 4


def test_eternal_tome_extends_only_caster_applied_effects():
    caster = make_battle("Caster", weapon=EternalTome())
    target = make_battle("Target")
    caster.status_effect["largeheal"] = {"duration": 2, "source": caster}
    target.status_effect["nightfall"] = {"duration": 3, "source": caster}
    target.status_effect["foreign"] = {"duration": 9, "source": object()}

    result = caster.weapon.on_spell_cast(caster, caster.spell, target, True)

    assert result == "Eternal Tome passive: Your spell effects last longer!"
    assert caster.status_effect["largeheal"]["duration"] == 5
    assert target.status_effect["nightfall"]["duration"] == 6
    assert target.status_effect["foreign"]["duration"] == 9


def test_elephant_hammer_returns_full_block_hook():
    defender = make_battle("Tank", weapon=ElephantHammer())
    assert defender.weapon.on_block(defender) == "fullblock"


def test_dark_blade_disables_healing_for_both_parties():
    attacker = make_battle("Attacker", weapon=DarkBlade())
    defender = make_battle("Defender")

    attacker.weapon.on_attack_success(attacker, defender, 10)

    assert attacker.can_heal is False
    assert defender.can_heal is False


def test_veyras_grimoire_trades_hp_for_mana_after_spell_cast():
    caster = make_battle("Mage", spell=Nightfall(), weapon=VeyrasGrimoire())
    target = make_battle("Target")

    ok, _ = caster.cast(target)

    assert ok is True
    assert caster.hp == 35
    assert caster.mana == 7


def test_bardoks_claymore_only_heals_when_origin_is_bardok():
    attacker = make_battle("Bardok", weapon=BardoksClaymore())
    defender = make_battle("Defender")

    dormant_result = attacker.weapon.on_attack_success(attacker, defender, 10)
    attacker.origin = "bardok"
    active_result = attacker.weapon.on_attack_success(attacker, defender, 10)

    assert "refuses to awaken" in dormant_result
    assert active_result == "Bardok's Claymore passive: Bardok siphons vitality and heals 4 HP"
    assert attacker.hp == 44


def test_lava_arena_damages_player_one_each_round():
    arena = LavaArena()
    manager = type("Manager", (), {"p1": make_battle("Hero")})()

    note = arena.on_round_start(manager)

    assert manager.p1.hp == 37
    assert note == "The lava scorches you for 3 HP 🔥"


def test_frozen_arena_adds_frost_each_round():
    arena = FrozenArena()
    manager = type("Manager", (), {"p1": make_battle("Hero")})()

    note = arena.on_round_start(manager)

    assert manager.p1.frost == 1
    assert "Frost stack" in note


def test_irritation_arena_rewards_predictable_player():
    player = make_battle("Hero")
    player.move_history.extend(["attack", "attack"])
    enemy = make_battle("Bardok")
    manager = type("Manager", (), {"p1": player, "p2": enemy})()

    note = IrritationArena().on_round_start(manager)

    assert enemy.attack == 30
    assert "predictability" in note


def test_bardok_ai_sets_origin_to_bardok():
    bardok = make_battle("Bardok")
    player = make_battle("Hero")

    BardokAI(bardok=bardok, player=player)

    assert bardok.origin == "bardok"
