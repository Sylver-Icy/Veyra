# ---- Battle lock registry (prevents concurrent battles per user) ----
ACTIVE_BATTLES = {}
# services/discord_battle/battle_simulation.py
import asyncio
import discord

from services.battle.battle_class import Battle
from services.battle.battlemanager_class import BattleManager
from services.battle.spell_class import Fireball, Heavyshot, ErdtreeBlessing, Nightfall, FrostBite, VeilOfDarkness, Earthquake
from services.battle.weapon_class import TrainingBlade, MoonSlasher, DarkBlade, ElephantHammer, EternalTome, VeyrasGrimoire, BardoksClaymore
from services.battle.loadout_services import fetch_loadout
from services.battle.battle_view import BattleRoundView, PvEBattleRoundView
from services.battle.veyra_ai import VeyraAI
from services.battle.campaign.bardok_ai import BardokAI
from services.battle.arena_class import LavaArena, FrozenArena, NullArena, IrritationArena
from services.economy_services import add_gold
from services.users_services import inc_battles_won

from services.battle.campaign.campaign_services import fetch_veyra_loadout, advance_campaign_stage, give_stage_rewards, stage_reward_details, get_campaign_stage

from utils.embeds.battleembed import (
    build_round_embed,
    build_result_embed,
    build_final_embed,
)

TIMEOUT_SECONDS = 50
TIMEOUT_PENALTY = 25
RESULT_DISPLAY_TIME = 12  # seconds before next round starts
weapon_map = {
    "moonslasher": MoonSlasher,
    "trainingblade": TrainingBlade,
    "darkblade": DarkBlade,
    "elephanthammer": ElephantHammer,
    "eternaltome": EternalTome,
    "veyrasgrimoire": VeyrasGrimoire,
    "bardoksclaymore": BardoksClaymore
}

spell_map = {
    "fireball": Fireball,
    "heavyshot": Heavyshot,
    "erdtreeblessing": ErdtreeBlessing,
    "nightfall": Nightfall,
    "frostbite": FrostBite,
    "veilofdarkness": VeilOfDarkness,
    "earthquake": Earthquake
}
async def start_battle_simulation(ctx, challenger: discord.User, target: discord.User, bet: int):
    """
    Orchestrates a full 1v1 battle flow in-channel.
    - New embed each round (previous deleted).
    - Auto-advance when both moves are locked.
    - 50s timeout => -25 HP penalty to the late player(s).
    - Ends immediately on death; announces winner and reward.
    """
    # ---- battle lock check (PvP) ----
    if challenger.id in ACTIVE_BATTLES or target.id in ACTIVE_BATTLES:
        await ctx.respond("❌ One of the players is already in a battle. Finish it before starting another.")
        return

    # lock both players
    ACTIVE_BATTLES[challenger.id] = "pvp"
    ACTIVE_BATTLES[target.id] = "pvp"
    # Initialize fighters from usernames
    weapon, spell = fetch_loadout(challenger.id)
    p1 = Battle(challenger.name, spell_map[spell](), weapon_map[weapon]())

    weapon, spell = fetch_loadout(target.id)
    p2 = Battle(target.name, spell_map[spell](), weapon_map[weapon]())
    bm = BattleManager(p1, p2)

    round_num = 1
    # Initial round announce
    round_embed = build_round_embed(round_num, p1, p2, challenger.name, target.name)
    view = BattleRoundView(p1_id=challenger.id, p2_id=target.id, timeout=TIMEOUT_SECONDS)
    cur_message = await ctx.channel.send(embed=round_embed, view=view)

    try:
        while True:
            # Wait for both moves or timeout
            try:
                await asyncio.wait_for(view.wait(), timeout=TIMEOUT_SECONDS)
            except asyncio.TimeoutError:
                # View might not have stopped;  handle penalties below
                pass

            # Determine selections and timeouts
            p1_move = view.moves.get(challenger.id)
            p2_move = view.moves.get(target.id)
            p1_timed_out = p1_move is None
            p2_timed_out = p2_move is None

            # Default any missing move to "attack" so the engine can still resolve the round
            if p1_move is None:
                p1_move = "attack"
            if p2_move is None:
                p2_move = "attack"

            # Execute + resolve the round via  ngine
            bm.execute_turn(p1_move, p2_move)
            result_text = bm.resolve_round()


            # Apply timeout penalties AFTER resolution
            penalty_notes = []

            if p1_timed_out:
                p1.hp = max(0, p1.hp - TIMEOUT_PENALTY)
                penalty_notes.append(f"{challenger.name} suffered an extra **-{TIMEOUT_PENALTY} HP** for hesitation.")
            if p2_timed_out:
                p2.hp = max(0, p2.hp - TIMEOUT_PENALTY)
                penalty_notes.append(f"{target.name} suffered an extra **-{TIMEOUT_PENALTY} HP** for hesitation.")

            # Trigger all  effects each round

            p1_penalty_notes = p1.proc_effect()
            p2_penalty_notes = p2.proc_effect()
            penalty_notes = (p1_penalty_notes or []) + (p2_penalty_notes or [])
            penalty_notes = [x for x in penalty_notes if isinstance(x, str) and x.strip()]



            # Replace the old round message with the result message
            result_embed = build_result_embed(
                round_num,
                challenger.name, target.name,
                p1_move, p2_move,
                result_text + (("\n" + "\n".join(penalty_notes)) if penalty_notes else ""),
                p1_timed_out, p2_timed_out
            )

            result_msg = await ctx.channel.send(embed=result_embed)

            # Delete the previous round's input embed immediately (we don’t need it anymore)
            with contextlib_silent():
                await cur_message.delete()

            # 🕒 Give players time to read the result before next round
            await asyncio.sleep(RESULT_DISPLAY_TIME)

            # Check for battle end conditions after displaying result
            if p1.hp <= 0 and p2.hp <= 0:
                final_embed = build_final_embed(None, None, bet, both_dead=True)
                await ctx.channel.send(embed=final_embed)
                return
            elif p1.hp <= 0:
                #P2 won give reward
                add_gold(target.id, int((bet * 2) * 0.9))
                inc_battles_won(target.id)
                final_embed = build_final_embed(target.name, challenger.name, bet)
                await ctx.channel.send(embed=final_embed)
                return
            elif p2.hp <= 0:
                add_gold(challenger.id, int((bet * 2) * 0.9))
                inc_battles_won(challenger.id)
                final_embed = build_final_embed(challenger.name, target.name, bet)
                await ctx.channel.send(embed=final_embed)
                return

            # Prepare for next round
            round_num += 1
            next_round_embed = build_round_embed(round_num, p1, p2, challenger.name, target.name)
            view = BattleRoundView(p1_id=challenger.id, p2_id=target.id, timeout=TIMEOUT_SECONDS)
            cur_message = await ctx.channel.send(embed=next_round_embed, view=view)

            # Now delete the result message to keep things clean
            with contextlib_silent():
                await result_msg.delete()

    finally:
        # ---- release battle locks (PvP) ----
        ACTIVE_BATTLES.pop(challenger.id, None)
        ACTIVE_BATTLES.pop(target.id, None)
        # Best-effort cleanup of any dangling views/messages
        try:
            if cur_message:
                await cur_message.edit(view=None)
        except Exception:
            pass


async def start_campaign_battle(ctx, player: discord.User):
    # ---- battle lock check (Campaign) ----
    if player.id in ACTIVE_BATTLES:
        await ctx.respond("❌ You are already in a battle. Finish it before starting another.")
        return

    # lock player
    ACTIVE_BATTLES[player.id] = "campaign"

    VEYRA_ID = 1
    weapon, spell = fetch_loadout(player.id)
    p1 = Battle(player.name, spell_map[spell](), weapon_map[weapon]())

    veyra_loadout = fetch_veyra_loadout(player.id)
    weapon_cls = weapon_map[veyra_loadout["weapon"]]
    spell_cls = spell_map[veyra_loadout["spell"]]

    stage = get_campaign_stage(player.id)

    enemy_name = "Veyra" if stage <= 10 else "Bardok"
    p2 = Battle(enemy_name, spell_cls(), weapon_cls())

    p2.hp += veyra_loadout.get("bonus_hp", 0)
    p2.mana += veyra_loadout.get("bonus_mana", 0)

    bm = BattleManager(p1, p2)

    # Assign arena based on campaign stage
    if stage == 13:
        bm.arena = IrritationArena()
    elif stage == 14:
        bm.arena = LavaArena()
    elif stage == 15:
        bm.arena = FrozenArena()
    else:
        bm.arena = NullArena()

    if stage <= 10:
        ai = VeyraAI(
            difficulty="normal",
            veyra=p2,
            player=p1
        )
    else:
        ai = BardokAI(
            bardok=p2,
            player=p1,
            stage=stage
        )

    round_num = 1
    round_embed = build_round_embed(round_num, p1, p2, player.name, enemy_name)

    view = PvEBattleRoundView(
        player_id=player.id,
        veyra_id=VEYRA_ID,
        ai_controller=ai,
        timeout=TIMEOUT_SECONDS
)

    cur_message = await ctx.channel.send(embed=round_embed, view=view)

    try:
        while True:
            try:
                await asyncio.wait_for(view.wait(), timeout=TIMEOUT_SECONDS)
            except asyncio.TimeoutError:
                pass

            p1_move = view.moves.get(player.id)
            p2_move = view.moves.get(VEYRA_ID)

            p1_timed_out = p1_move is None


            if p1_move is None:
                p1_move = "attack"
            if p2_move is None:
                p2_move = "attack"

            bm.execute_turn(p1_move, p2_move)
            result_text = bm.resolve_round()

            penalty_notes = []

            if p1_timed_out:
                p1.hp = max(0, p1.hp - TIMEOUT_PENALTY)
                penalty_notes.append(f"{player.name} suffered an extra **-{TIMEOUT_PENALTY} HP** for hesitation.")

            p1_penalty_notes = p1.proc_effect()
            p2_penalty_notes = p2.proc_effect()
            penalty_notes = (p1_penalty_notes or []) + (p2_penalty_notes or [])
            penalty_notes = [x for x in penalty_notes if isinstance(x, str) and x.strip()]

            result_embed = build_result_embed(
                round_num,
                player.name,
                enemy_name,
                p1_move,
                p2_move,
                result_text + (("\n" + "\n".join(penalty_notes)) if penalty_notes else ""),
                p1_timed_out,
                False
            )

            result_msg = await ctx.channel.send(embed=result_embed)

            with contextlib_silent():
                await cur_message.delete()

            await asyncio.sleep(RESULT_DISPLAY_TIME)

            if p1.hp <= 0:
                final_embed = build_final_embed(enemy_name, player.name, 0)
                await ctx.channel.send(embed=final_embed)
                return
            elif p2.hp <= 0:
                final_embed = build_final_embed(player.name, enemy_name, 0)
                await ctx.channel.send(embed=final_embed)
                reward_string = stage_reward_details(player.id)
                await ctx.followup.send(f"🏆 {player.name} advanced to the next campaign stage!\n{reward_string}")
                give_stage_rewards(player.id)
                advance_campaign_stage(player.id)
                return

            round_num += 1
            next_round_embed = build_round_embed(round_num, p1, p2, player.name, enemy_name)

            view = PvEBattleRoundView(
            player_id=player.id,
            veyra_id=VEYRA_ID,
            ai_controller=ai,
            timeout=TIMEOUT_SECONDS
)

            cur_message = await ctx.channel.send(embed=next_round_embed, view=view)

            with contextlib_silent():
                await result_msg.delete()

    finally:
        # ---- release battle lock (Campaign) ----
        ACTIVE_BATTLES.pop(player.id, None)
        try:
            if cur_message:
                await cur_message.edit(view=None)
        except Exception:
            pass


# ---- tiny helper: suppress deletes when already deleted ----
from contextlib import contextmanager

@contextmanager
def contextlib_silent():
    try:
        yield
    except Exception:
        pass
