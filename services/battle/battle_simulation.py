# ---- Battle lock registry (prevents concurrent battles per user) ----
ACTIVE_BATTLES = {}

import asyncio
from contextlib import contextmanager

import discord

from services.battle.battle_class import Battle
from services.battle.battle_view import BattleRoundView, PvEBattleRoundView
from services.battle.battlemanager_class import BattleManager
from services.battle.campaign.campaign_services import fetch_veyra_loadout, get_campaign_stage
from services.battle.content_registry import CONTENT_REGISTRY
from services.battle.session_runner import BattleSession
from services.battle.settlement_services import SettlementService
from services.battle.loadout_services import fetch_loadout
from utils.embeds.battleembed import build_final_embed, build_result_embed, build_round_embed

TIMEOUT_SECONDS = 50
TIMEOUT_PENALTY = 25
RESULT_DISPLAY_TIME = 12


def _build_player_fighter(user_id: int, name: str) -> Battle:
    weapon_key, spell_key = fetch_loadout(user_id)
    return Battle(
        name,
        CONTENT_REGISTRY.create_spell(spell_key),
        CONTENT_REGISTRY.create_weapon(weapon_key),
    )


def _build_campaign_enemy(player_id: int):
    stage = get_campaign_stage(player_id)
    enemy_key = "veyra" if stage <= 10 else "bardok"
    enemy_name = "Veyra" if enemy_key == "veyra" else "Bardok"
    loadout = fetch_veyra_loadout(player_id)
    enemy = Battle(
        enemy_name,
        CONTENT_REGISTRY.create_spell(loadout["spell"]),
        CONTENT_REGISTRY.create_weapon(loadout["weapon"]),
    )
    enemy.hp += loadout.get("bonus_hp", 0)
    enemy.mana += loadout.get("bonus_mana", 0)
    return stage, enemy_key, enemy_name, enemy


def _arena_key_for_stage(stage: int) -> str:
    if stage == 13:
        return "irritation"
    if stage == 14:
        return "lava"
    if stage == 15:
        return "frozen"
    return "null"


async def _run_battle_session(
    *,
    ctx,
    session: BattleSession,
    round_names: tuple[str, str],
    build_view,
    extract_moves,
    result_display_time: int,
    finalizer,
):
    round_num = 1
    cur_message = None
    result_msg = None

    try:
        view = build_view()
        cur_message = await ctx.channel.send(
            embed=build_round_embed(round_num, session.p1, session.p2, round_names[0], round_names[1]),
            view=view,
        )

        while True:
            try:
                await asyncio.wait_for(view.wait(), timeout=TIMEOUT_SECONDS)
            except asyncio.TimeoutError:
                pass

            p1_move, p2_move, p1_timed_out, p2_timed_out = extract_moves(view)
            if p1_move is None:
                p1_move = "attack"
            if p2_move is None:
                p2_move = "attack"

            outcome = session.process_round(
                round_number=round_num,
                p1_move=p1_move,
                p2_move=p2_move,
                p1_timed_out=p1_timed_out,
                p2_timed_out=p2_timed_out,
                p1_name=round_names[0],
                p2_name=round_names[1],
            )

            result_msg = await ctx.channel.send(
                embed=build_result_embed(
                    round_num,
                    round_names[0],
                    round_names[1],
                    outcome.p1_move,
                    outcome.p2_move,
                    outcome.result_text,
                    outcome.p1_timed_out,
                    outcome.p2_timed_out,
                )
            )

            with contextlib_silent():
                await cur_message.delete()

            await asyncio.sleep(result_display_time)

            result_state = session.get_result_state()
            if result_state.finished:
                await finalizer(result_state)
                return

            round_num += 1
            view = build_view()
            cur_message = await ctx.channel.send(
                embed=build_round_embed(round_num, session.p1, session.p2, round_names[0], round_names[1]),
                view=view,
            )

            with contextlib_silent():
                await result_msg.delete()
                result_msg = None

    finally:
        try:
            if cur_message:
                await cur_message.edit(view=None)
        except Exception:
            pass


async def start_battle_simulation(ctx, challenger: discord.User, target: discord.User, bet: int):
    if challenger.id in ACTIVE_BATTLES or target.id in ACTIVE_BATTLES:
        await ctx.respond("❌ One of the players is already in a battle. Finish it before starting another.")
        return

    ACTIVE_BATTLES[challenger.id] = "pvp"
    ACTIVE_BATTLES[target.id] = "pvp"

    try:
        session = BattleSession(
            BattleManager(
                _build_player_fighter(challenger.id, challenger.name),
                _build_player_fighter(target.id, target.name),
            ),
            timeout_penalty=TIMEOUT_PENALTY,
        )

        def build_view():
            return BattleRoundView(
                p1_id=challenger.id,
                p2_id=target.id,
                timeout=TIMEOUT_SECONDS,
            )

        def extract_moves(view):
            p1_move = view.moves.get(challenger.id)
            p2_move = view.moves.get(target.id)
            return p1_move, p2_move, p1_move is None, p2_move is None

        async def finalizer(_result_state):
            settlement = SettlementService.resolve_pvp(
                challenger_id=challenger.id,
                challenger_name=challenger.name,
                target_id=target.id,
                target_name=target.name,
                bet=bet,
                p1=session.p1,
                p2=session.p2,
            )
            await ctx.channel.send(
                embed=build_final_embed(
                    settlement.winner_name,
                    settlement.loser_name,
                    bet,
                    both_dead=settlement.both_dead,
                )
            )

        await _run_battle_session(
            ctx=ctx,
            session=session,
            round_names=(challenger.name, target.name),
            build_view=build_view,
            extract_moves=extract_moves,
            result_display_time=RESULT_DISPLAY_TIME,
            finalizer=finalizer,
        )

    finally:
        ACTIVE_BATTLES.pop(challenger.id, None)
        ACTIVE_BATTLES.pop(target.id, None)


async def start_campaign_battle(ctx, player: discord.User, result_display_time: int = 12):
    if result_display_time is None:
        result_display_time = 12

    if player.id in ACTIVE_BATTLES:
        await ctx.respond("❌ You are already in a battle. Finish it before starting another.")
        return

    ACTIVE_BATTLES[player.id] = "campaign"
    VEYRA_ID = 1

    try:
        stage, enemy_key, enemy_name, enemy = _build_campaign_enemy(player.id)
        player_fighter = _build_player_fighter(player.id, player.name)
        manager = BattleManager(player_fighter, enemy)
        manager.arena = CONTENT_REGISTRY.create_arena(_arena_key_for_stage(stage))

        ai = CONTENT_REGISTRY.create_npc_ai(
            enemy_key,
            fighter=enemy,
            opponent=player_fighter,
            stage=stage,
            difficulty="normal",
        )
        session = BattleSession(manager, timeout_penalty=TIMEOUT_PENALTY)

        def build_view():
            return PvEBattleRoundView(
                player_id=player.id,
                veyra_id=VEYRA_ID,
                ai_controller=ai,
                timeout=TIMEOUT_SECONDS,
            )

        def extract_moves(view):
            p1_move = view.moves.get(player.id)
            p2_move = view.moves.get(VEYRA_ID)
            return p1_move, p2_move, p1_move is None, False

        async def finalizer(_result_state):
            settlement = SettlementService.resolve_campaign(
                player_id=player.id,
                player_name=player.name,
                enemy_name=enemy_name,
                stage=stage,
                p1=session.p1,
                p2=session.p2,
            )
            await ctx.channel.send(
                embed=build_final_embed(
                    settlement.winner_name,
                    settlement.loser_name,
                    0,
                    both_dead=settlement.both_dead,
                )
            )
            if settlement.followup_message:
                await ctx.followup.send(settlement.followup_message)

        await _run_battle_session(
            ctx=ctx,
            session=session,
            round_names=(player.name, enemy_name),
            build_view=build_view,
            extract_moves=extract_moves,
            result_display_time=result_display_time,
            finalizer=finalizer,
        )

    finally:
        ACTIVE_BATTLES.pop(player.id, None)


@contextmanager
def contextlib_silent():
    try:
        yield
    except Exception:
        pass
