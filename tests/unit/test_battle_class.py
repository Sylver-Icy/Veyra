import itertools

from services.battle import battle_class as battle_module
from services.battle.battle_class import Battle
from services.battle.spell_class import Nightfall
from services.battle.weapon_class import ElephantHammer, TrainingBlade, VeyrasGrimoire


def make_battle(name="Tester", spell=None, weapon=None):
    return Battle(name, spell or Nightfall(), weapon or TrainingBlade())


def sequence(values):
    iterator = itertools.cycle(values)
    return lambda *_args, **_kwargs: next(iterator)


def test_deal_dmg_applies_damage_and_weapon_hook():
    attacker = make_battle("Attacker")
    defender = make_battle("Defender")

    damage = attacker.deal_dmg(defender)

    assert damage == 10
    assert defender.hp == 30
    assert attacker.attack == 11
    assert attacker.log[-1] == "Training Blade passive: Attacker's attack increased by 1"


def test_deal_dmg_respects_blocking_stances():
    attacker = make_battle("Attacker")
    defender = make_battle("Defender")
    defender.current_stance = "block"

    damage = attacker.deal_dmg(defender)

    assert damage == 10
    assert defender.hp == 40
    assert attacker.attack == 10


def test_deal_dmg_is_reduced_by_veil_of_darkness():
    attacker = make_battle("Attacker")
    defender = make_battle("Defender")
    defender.status_effect["veilofdarkness"] = {"duration": 2, "source": defender}

    damage = attacker.deal_dmg(defender)

    assert damage == 4
    assert defender.hp == 36


def test_block_can_full_block_with_elephant_hammer(monkeypatch):
    defender = make_battle("Defender", weapon=ElephantHammer())
    attacker = make_battle("Attacker")
    attacker.current_stance = "attack"
    monkeypatch.setattr(battle_module.random, "randint", lambda *_args, **_kwargs: 15)

    result = defender.block(attacker, 10)

    assert result == {"status": "fullsuccess", "defense_buff": 15}
    assert defender.defense == 40


def test_block_regular_success_reduces_damage(monkeypatch):
    defender = make_battle("Defender")
    attacker = make_battle("Attacker")
    attacker.current_stance = "attack"
    attacker.speed = 14
    defender.speed = 10
    monkeypatch.setattr(battle_module.random, "randint", sequence([50, 13]))

    result = defender.block(attacker, 10)

    assert result == {"status": "success", "defense_buff": 13}
    assert defender.hp == 37
    assert defender.defense == 23


def test_block_can_fail_from_speed_roll(monkeypatch):
    defender = make_battle("Defender")
    attacker = make_battle("Attacker")
    attacker.current_stance = "attack"
    attacker.speed = 20
    defender.speed = 10
    monkeypatch.setattr(battle_module.random, "randint", lambda *_args, **_kwargs: 1)

    result = defender.block(attacker, 10)

    assert result == {"status": "failed"}
    assert defender.hp == 40


def test_block_wrong_guess_lowers_defense(monkeypatch):
    defender = make_battle("Defender")
    attacker = make_battle("Attacker")
    attacker.current_stance = "recover"
    monkeypatch.setattr(battle_module.random, "randint", lambda *_args, **_kwargs: 9)

    result = defender.block(attacker, 0)

    assert result == {"status": "wrong_guess", "defense_debuff": 9}
    assert defender.defense == 1


def test_counter_reflects_damage_against_attack():
    defender = make_battle("Defender")
    attacker = make_battle("Attacker")
    attacker.current_stance = "attack"

    reflected = defender.counter(attacker, 10)

    assert reflected == 5
    assert attacker.hp == 35


def test_counter_failure_converts_missing_stats_into_hp_loss(monkeypatch):
    defender = make_battle("Defender")
    attacker = make_battle("Attacker")
    attacker.current_stance = "recover"
    defender.speed = 2
    defender.defense = 5
    monkeypatch.setattr(battle_module.random, "randint", sequence([3, 12]))

    result = defender.counter(attacker, 0)

    assert result == {"hp_drain": 15, "speed_drain": 3, "defense_drain": 12}
    assert defender.hp == 25


def test_regen_cycles_hp_then_mana_when_safe(monkeypatch):
    fighter = make_battle("Healer")
    target = make_battle("Target")
    target.current_stance = "block"
    monkeypatch.setattr(battle_module.random, "randint", sequence([8, 4]))

    hp_regen = fighter.regen(target)
    mana_regen = fighter.regen(target)

    assert hp_regen == {"status": "success", "hp_recovered": 8}
    assert mana_regen == {"status": "success", "mana_recovered": 4}
    assert fighter.hp == 48
    assert fighter.mana == 14


def test_regen_blocked_when_healing_is_disabled():
    fighter = make_battle("Healer")
    target = make_battle("Target")
    target.current_stance = "block"
    fighter.can_heal = False

    result = fighter.regen(target)

    assert result == {"status": "blocked"}
    assert fighter.regen_state == "mana"


def test_regen_is_interrupted_by_aggressive_stances():
    fighter = make_battle("Healer")
    target = make_battle("Target")
    target.current_stance = "attack"

    result = fighter.regen(target)

    assert result == {"status": "intrupted"}
    assert fighter.regen_state == "mana"


def test_cast_triggers_weapon_spell_hook():
    caster = make_battle("Mage", weapon=VeyrasGrimoire())
    target = make_battle("Target")

    ok, _ = caster.cast(target)

    assert ok is True
    assert caster.hp == 35
    assert caster.mana == 7
    assert "nightfall" in target.status_effect


def test_proc_effect_heals_expires_effect_and_triggers_frost(monkeypatch):
    fighter = make_battle("Target")
    fighter.hp = 20
    fighter.status_effect["largeheal"] = {"duration": 1, "source": fighter}
    fighter.frost = 10
    monkeypatch.setattr(battle_module.random, "choice", lambda values: values[0])

    logs = fighter.proc_effect()

    assert fighter.hp == 12
    assert fighter.frost == 0
    assert "largeheal" not in fighter.status_effect
    assert any("healed 4 hp" in log for log in logs)
    assert any("no longer affected by largeheal" in log for log in logs)
    assert any("Frostbite triggers" in log for log in logs)


def test_proc_effect_applies_nightfall_stat_drop(monkeypatch):
    fighter = make_battle("Target")
    fighter.status_effect["nightfall"] = {"duration": 2, "source": fighter}
    monkeypatch.setattr(battle_module.random, "choice", lambda values: "attack")

    logs = fighter.proc_effect()

    assert fighter.attack == 9
    assert fighter.status_effect["nightfall"]["duration"] == 1
    assert "attack drops by 1" in logs[0]


def test_set_stance_ignores_invalid_values():
    fighter = make_battle()

    fighter.set_stance("attack")
    fighter.set_stance("dance")

    assert fighter.current_stance == "attack"


def test_calculate_fail_chance_only_penalizes_slower_defender():
    assert Battle.calculate_fail_chance(20, 10) == 25
    assert Battle.calculate_fail_chance(10, 20) == 0
