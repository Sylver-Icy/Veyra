import sys
import types

sessionmaker_stub = types.ModuleType("database.sessionmaker")
sessionmaker_stub.Session = lambda: None
sys.modules["database.sessionmaker"] = sessionmaker_stub

from services.battle.campaign import campaign_services


def test_stage_10_unlock_reward_grants_veyras_grimoire_shard(monkeypatch):
    calls = []

    monkeypatch.setattr(campaign_services, "get_campaign_stage", lambda user_id: 10)
    monkeypatch.setattr(campaign_services, "give_item", lambda *args: calls.append(args))

    campaign_services.give_stage_rewards(123)

    assert calls == [(123, 3006, 1, True)]


def test_stage_10_unlock_reward_details_mentions_signature_shard(monkeypatch):
    monkeypatch.setattr(campaign_services, "get_campaign_stage", lambda user_id: 10)

    details = campaign_services.stage_reward_details(123)

    assert "signature grimoire" in details
    assert "Veyra's Grimoire Shard" in details


def test_stage_15_reward_grants_bardok_shard_after_normal_reward(monkeypatch):
    calls = []

    monkeypatch.setattr(campaign_services, "get_campaign_stage", lambda user_id: 15)
    monkeypatch.setattr(campaign_services, "give_item", lambda *args: calls.append(args))

    campaign_services.give_stage_rewards(123)

    assert calls == [
        (123, 199, 1, True),
        (123, 3007, 1, True),
    ]
