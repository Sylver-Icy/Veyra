from itertools import product

import pytest

from services.battle.arena_class import LavaArena
from services.battle.battle_class import Battle
from services.battle.battlemanager_class import BattleManager
from services.battle.spell_class import Nightfall
from services.battle.weapon_class import MoonSlasher, TrainingBlade


VALID_MOVES = ("attack", "block", "counter", "recover", "cast")


def make_battle(name="Tester", spell=None, weapon=None):
    return Battle(name, spell or Nightfall(), weapon or TrainingBlade())


@pytest.mark.parametrize(("p1_move", "p2_move"), product(VALID_MOVES, repeat=2))
def test_resolve_round_handles_every_valid_stance_pair(p1_move, p2_move):
    manager = BattleManager(make_battle("P1"), make_battle("P2"))

    manager.execute_turn(p1_move, p2_move)
    result = manager.resolve_round()

    assert isinstance(result, str)
    assert result != "No valid moves resolved this round."


def test_execute_turn_sets_stances_and_histories():
    p1 = make_battle("P1")
    p2 = make_battle("P2")
    manager = BattleManager(p1, p2)

    manager.execute_turn("attack", "block")

    assert p1.current_stance == "attack"
    assert p2.current_stance == "block"
    assert list(p1.move_history) == ["attack"]
    assert list(p2.move_history) == ["block"]


def test_attack_vs_attack_uses_speed_order():
    p1 = make_battle("Fast")
    p2 = make_battle("Slow")
    p1.speed = 20
    p2.speed = 10
    manager = BattleManager(p1, p2)
    manager.execute_turn("attack", "attack")

    result = manager.resolve_round()

    assert "Fast is faster" in result
    assert p1.hp == 30
    assert p2.hp == 30


def test_cast_vs_cast_same_speed_interrupts_both_players():
    p1 = make_battle("P1")
    p2 = make_battle("P2")
    manager = BattleManager(p1, p2)
    manager.execute_turn("cast", "cast")

    result = manager.resolve_round()

    assert "same speed" in result
    assert p1.mana == 5
    assert p2.mana == 5


def test_cast_vs_cast_faster_player_gets_spell_off():
    p1 = make_battle("Fast")
    p2 = make_battle("Slow")
    p1.speed = 20
    manager = BattleManager(p1, p2)
    manager.execute_turn("cast", "cast")

    result = manager.resolve_round()

    assert "Due to higher speed Fast" in result
    assert "nightfall" in p2.status_effect
    assert p2.mana == 5


def test_round_result_includes_arena_note_prefix():
    manager = BattleManager(make_battle("P1"), make_battle("P2"))
    manager.arena = LavaArena()
    manager.execute_turn("block", "block")

    result = manager.resolve_round()

    assert result.startswith("The lava scorches you for 3 HP")
    assert manager.p1.hp == 30


def test_resolve_round_honors_preexisting_dead_player():
    p1 = make_battle("P1")
    p2 = make_battle("P2")
    p2.hp = 0
    manager = BattleManager(p1, p2)

    result = manager.resolve_round()

    assert result == "P2 has fallen. P1 wins!"


def test_attack_vs_counter_reflects_damage_without_direct_hit():
    p1 = make_battle("Attacker")
    p2 = make_battle("Counter")
    manager = BattleManager(p1, p2)
    manager.execute_turn("attack", "counter")

    result = manager.resolve_round()

    assert "countered dealing 5 damage back" in result
    assert p1.hp == 35
    assert p2.hp == 40


def test_recover_vs_block_returns_recovery_resolution():
    p1 = make_battle("Recoverer")
    p2 = make_battle("Blocker", weapon=MoonSlasher())
    manager = BattleManager(p1, p2)
    manager.execute_turn("recover", "block")

    result = manager.resolve_round()

    assert "successfully got" in result
