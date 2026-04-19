from dataclasses import dataclass


@dataclass
class SettlementResult:
    winner_name: str | None
    loser_name: str | None
    both_dead: bool = False
    reward_summary: str | None = None
    followup_message: str | None = None


def _add_gold(*args, **kwargs):
    from services.economy_services import add_gold

    return add_gold(*args, **kwargs)


def _inc_battles_won(*args, **kwargs):
    from services.users_services import inc_battles_won

    return inc_battles_won(*args, **kwargs)


def _update_quest_progress(*args, **kwargs):
    from services.quest_services import update_quest_progress

    return update_quest_progress(*args, **kwargs)


def _decrease_quest_progress(*args, **kwargs):
    from services.quest_services import decrease_quest_progress

    return decrease_quest_progress(*args, **kwargs)


def _stage_reward_details(*args, **kwargs):
    from services.battle.campaign.campaign_services import stage_reward_details

    return stage_reward_details(*args, **kwargs)


def _give_stage_rewards(*args, **kwargs):
    from services.battle.campaign.campaign_services import give_stage_rewards

    return give_stage_rewards(*args, **kwargs)


def _advance_campaign_stage(*args, **kwargs):
    from services.battle.campaign.campaign_services import advance_campaign_stage

    return advance_campaign_stage(*args, **kwargs)


def _create_game_event(*args, **kwargs):
    from services.game_events_services import create_game_event

    return create_game_event(*args, **kwargs)


class SettlementService:
    @staticmethod
    def resolve_pvp(*, challenger_id: int, challenger_name: str, target_id: int, target_name: str, bet: int, p1, p2) -> SettlementResult:
        if p1.hp <= 0 and p2.hp <= 0:
            return SettlementResult(winner_name=None, loser_name=None, both_dead=True)

        if p1.hp <= 0:
            _add_gold(target_id, int((bet * 2) * 0.9))
            _inc_battles_won(target_id)
            _update_quest_progress(target_id, "BATTLE_WIN", 1)
            _update_quest_progress(target_id, "BATTLE_WIN_STREAK", 1)
            _decrease_quest_progress(challenger_id, "BATTLE_WIN_STREAK")
            return SettlementResult(winner_name=target_name, loser_name=challenger_name)

        _add_gold(challenger_id, int((bet * 2) * 0.9))
        _inc_battles_won(challenger_id)
        _update_quest_progress(challenger_id, "BATTLE_WIN", 1)
        _update_quest_progress(challenger_id, "BATTLE_WIN_STREAK", 1)
        _decrease_quest_progress(target_id, "BATTLE_WIN_STREAK")
        return SettlementResult(winner_name=challenger_name, loser_name=target_name)

    @staticmethod
    def resolve_campaign(*, player_id: int, player_name: str, enemy_name: str, stage: int, p1, p2) -> SettlementResult:
        if p1.hp <= 0:
            return SettlementResult(winner_name=enemy_name, loser_name=player_name)

        reward_string = _stage_reward_details(player_id)
        _give_stage_rewards(player_id)
        _advance_campaign_stage(player_id)
        _update_quest_progress(player_id, "CAMPAIGN_WIN", 1)

        next_stage = min(stage + 1, 16)
        if next_stage >= 16:
            summary = f"Defeated {enemy_name} and finished the campaign."
        else:
            summary = f"Defeated {enemy_name} in campaign stage {stage} and advanced to stage {next_stage}."

        _create_game_event(
            player_id,
            "campaign_progress",
            summary,
            {
                "enemy_name": enemy_name,
                "cleared_stage": stage,
                "next_stage": next_stage,
                "reward_summary": reward_string,
            },
        )

        return SettlementResult(
            winner_name=player_name,
            loser_name=enemy_name,
            reward_summary=reward_string,
            followup_message=f"🏆 {player_name} advanced to the next campaign stage!\n{reward_string}",
        )
