from services.battle.battle_class import Battle
from services.battle.battlemanager_class import BattleManager
from services.battle.session_runner import BattleSession
from services.battle.settlement_services import SettlementService
from services.battle.spell_class import Nightfall
from services.battle.weapon_class import TrainingBlade


def make_battle(name="Tester", spell=None, weapon=None):
    return Battle(name, spell or Nightfall(), weapon or TrainingBlade())


def test_battle_session_process_round_collects_resolution_and_penalties():
    manager = BattleManager(make_battle("P1"), make_battle("P2"))
    session = BattleSession(manager, timeout_penalty=25)

    outcome = session.process_round(
        round_number=1,
        p1_move="attack",
        p2_move="attack",
        p1_timed_out=True,
        p2_timed_out=False,
        p1_name="P1",
        p2_name="P2",
    )

    assert outcome.round_number == 1
    assert outcome.p1_timed_out is True
    assert "both attacked at same time" in outcome.resolution.text
    assert all("hesitation" not in note for note in outcome.penalty_notes)
    assert session.p1.hp == 5


def test_battle_session_get_result_state_handles_wins_and_double_ko():
    manager = BattleManager(make_battle("P1"), make_battle("P2"))
    session = BattleSession(manager)

    session.p1.hp = 0
    session.p2.hp = 0
    both_dead = session.get_result_state()

    session.p1.hp = 10
    session.p2.hp = 0
    p1_win = session.get_result_state()

    assert both_dead.finished is True
    assert both_dead.both_dead is True
    assert p1_win.finished is True
    assert p1_win.winner is session.p1
    assert p1_win.loser is session.p2


def test_pvp_settlement_pays_winner_and_updates_progress(monkeypatch):
    calls = []
    monkeypatch.setattr("services.battle.settlement_services._add_gold", lambda *args: calls.append(("gold", args)))
    monkeypatch.setattr("services.battle.settlement_services._inc_battles_won", lambda *args: calls.append(("wins", args)))
    monkeypatch.setattr("services.battle.settlement_services._update_quest_progress", lambda *args: calls.append(("quest", args)))
    monkeypatch.setattr("services.battle.settlement_services._decrease_quest_progress", lambda *args: calls.append(("decrease", args)))

    p1 = make_battle("Challenger")
    p2 = make_battle("Target")
    p1.hp = 0

    result = SettlementService.resolve_pvp(
        challenger_id=1,
        challenger_name="Challenger",
        target_id=2,
        target_name="Target",
        bet=100,
        p1=p1,
        p2=p2,
    )

    assert result.winner_name == "Target"
    assert ("gold", (2, 180)) in calls
    assert ("wins", (2,)) in calls
    assert ("quest", (2, "BATTLE_WIN", 1)) in calls
    assert ("quest", (2, "BATTLE_WIN_STREAK", 1)) in calls
    assert ("decrease", (1, "BATTLE_WIN_STREAK")) in calls


def test_pvp_settlement_handles_double_ko_without_side_effects(monkeypatch):
    monkeypatch.setattr("services.battle.settlement_services._add_gold", lambda *args: (_ for _ in ()).throw(AssertionError("unexpected payout")))
    monkeypatch.setattr("services.battle.settlement_services._inc_battles_won", lambda *args: (_ for _ in ()).throw(AssertionError("unexpected win update")))
    monkeypatch.setattr("services.battle.settlement_services._update_quest_progress", lambda *args: (_ for _ in ()).throw(AssertionError("unexpected quest update")))
    monkeypatch.setattr("services.battle.settlement_services._decrease_quest_progress", lambda *args: (_ for _ in ()).throw(AssertionError("unexpected quest decrease")))

    p1 = make_battle("Challenger")
    p2 = make_battle("Target")
    p1.hp = 0
    p2.hp = 0

    result = SettlementService.resolve_pvp(
        challenger_id=1,
        challenger_name="Challenger",
        target_id=2,
        target_name="Target",
        bet=100,
        p1=p1,
        p2=p2,
    )

    assert result.both_dead is True
    assert result.winner_name is None


def test_campaign_settlement_returns_followup_and_event_summary(monkeypatch):
    calls = []
    monkeypatch.setattr("services.battle.settlement_services._stage_reward_details", lambda player_id: f"Reward for {player_id}")
    monkeypatch.setattr("services.battle.settlement_services._give_stage_rewards", lambda *args: calls.append(("rewards", args)))
    monkeypatch.setattr("services.battle.settlement_services._advance_campaign_stage", lambda *args: calls.append(("advance", args)))
    monkeypatch.setattr("services.battle.settlement_services._update_quest_progress", lambda *args: calls.append(("quest", args)))
    monkeypatch.setattr("services.battle.settlement_services._create_game_event", lambda *args: calls.append(("event", args)))

    p1 = make_battle("Player")
    p2 = make_battle("Bardok")
    p2.hp = 0

    result = SettlementService.resolve_campaign(
        player_id=7,
        player_name="Player",
        enemy_name="Bardok",
        stage=12,
        p1=p1,
        p2=p2,
    )

    assert result.winner_name == "Player"
    assert result.loser_name == "Bardok"
    assert result.reward_summary == "Reward for 7"
    assert result.followup_message == "🏆 Player advanced to the next campaign stage!\nReward for 7"
    assert ("rewards", (7,)) in calls
    assert ("advance", (7,)) in calls
    assert ("quest", (7, "CAMPAIGN_WIN", 1)) in calls
    assert calls[-1][0] == "event"
