from services.battle.arena_class import NullArena
from services.battle.battle_class import Battle
from services.battle.campaign.bardok_ai import BardokAI
from services.battle.campaign.npcai import BaseAI
from services.battle.spell_class import Earthquake, Fireball, FrostBite, Nightfall
from services.battle.veyra_ai import VeyraAI
from services.battle.weapon_class import BardoksClaymore, MoonSlasher, TrainingBlade


def make_battle(name="Tester", spell=None, weapon=None):
    return Battle(name, spell or Nightfall(), weapon or TrainingBlade())


def test_base_ai_weighted_choice_uses_expected_move_order(monkeypatch):
    captured = {}
    ai = BaseAI(fighter=make_battle("NPC"), opponent=make_battle("Player"))

    def fake_choices(options, weights, k):
        captured["options"] = options
        captured["weights"] = weights
        captured["k"] = k
        return ["cast"]

    monkeypatch.setattr("services.battle.campaign.npcai.random.choices", fake_choices)

    result = ai.weighted_choice([1, 2, 3, 4, 5])

    assert result == "cast"
    assert captured == {
        "options": ["attack", "block", "counter", "recover", "cast"],
        "weights": [1, 2, 3, 4, 5],
        "k": 1,
    }


def test_veyra_ai_directly_casts_when_no_other_branch_applies():
    veyra = make_battle("Veyra", spell=Fireball())
    player = make_battle("Player")
    veyra.mana = 20
    veyra.speed = 20
    player.speed = 10

    ai = VeyraAI(veyra=veyra, player=player)

    assert ai.choose_move() == "cast"


def test_veyra_ai_no_history_path_resets_non_history_weights(monkeypatch):
    captured = {}
    veyra = make_battle("Veyra", spell=Fireball())
    player = make_battle("Player")
    veyra.mana = 20
    veyra.speed = 10
    player.speed = 10
    ai = VeyraAI(veyra=veyra, player=player)

    monkeypatch.setattr(
        ai,
        "weighted_choice",
        lambda weights: captured.setdefault("weights", weights) or "attack",
    )

    ai.choose_move()

    assert captured["weights"] == [25, 25, 25, 25, 45]


def test_veyra_ai_biases_against_attack_spam(monkeypatch):
    captured = {}
    veyra = make_battle("Veyra")
    player = make_battle("Player")
    veyra.mana = 0
    player.move_history.extend(["attack", "attack", "attack", "block"])
    ai = VeyraAI(veyra=veyra, player=player)

    monkeypatch.setattr(
        ai,
        "weighted_choice",
        lambda weights: captured.setdefault("weights", weights) or "attack",
    )

    ai.choose_move()

    assert captured["weights"] == [25, 35, 45, 15, 0]


def test_bardok_ai_casts_earthquake_when_player_is_turtling():
    bardok = make_battle("Bardok", spell=Earthquake(), weapon=BardoksClaymore())
    player = make_battle("Player")
    bardok.mana = 20
    bardok.speed = 15
    player.speed = 10
    player.defense = 12
    ai = BardokAI(bardok=bardok, player=player, stage=12)

    assert ai.choose_move() == "cast"


def test_bardok_ai_stage_13_punishes_predictable_history(monkeypatch):
    captured = {}
    bardok = make_battle("Bardok", spell=Nightfall(), weapon=BardoksClaymore())
    player = make_battle("Player")
    bardok.mana = 0
    player.move_history.extend(["attack"])
    ai = BardokAI(bardok=bardok, player=player, stage=13)

    monkeypatch.setattr(
        ai,
        "weighted_choice",
        lambda weights: captured.setdefault("weights", weights) or "attack",
    )

    ai.choose_move()

    assert captured["weights"] == [35, 35, 35, 95, 0]


def test_bardok_ai_no_history_path_resets_weapon_bias(monkeypatch):
    captured = {}
    bardok = make_battle("Bardok", spell=Nightfall(), weapon=MoonSlasher())
    player = make_battle("Player")
    bardok.mana = 0
    ai = BardokAI(bardok=bardok, player=player, stage=11)

    monkeypatch.setattr(
        ai,
        "weighted_choice",
        lambda weights: captured.setdefault("weights", weights) or "attack",
    )

    ai.choose_move()

    assert captured["weights"] == [25, 25, 25, 25, 0]


def test_null_arena_has_no_round_effect():
    arena = NullArena()
    manager = type("Manager", (), {"p1": make_battle("Hero")})()

    assert arena.on_round_start(manager) is None
