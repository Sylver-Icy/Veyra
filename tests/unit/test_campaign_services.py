from services.battle.campaign import campaign_services


def test_stage_10_unlock_reward_does_not_try_to_grant_inventory_item(monkeypatch):
    calls = []

    monkeypatch.setattr(campaign_services, "get_campaign_stage", lambda user_id: 10)
    monkeypatch.setattr(campaign_services, "give_item", lambda *args: calls.append(args))

    campaign_services.give_stage_rewards(123)

    assert calls == []


def test_stage_10_unlock_reward_details_mentions_signature_unlock(monkeypatch):
    monkeypatch.setattr(campaign_services, "get_campaign_stage", lambda user_id: 10)

    details = campaign_services.stage_reward_details(123)

    assert "signature grimoire" in details
    assert "spell bound within it" in details
