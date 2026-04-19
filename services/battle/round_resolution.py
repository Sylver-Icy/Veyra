from services.battle.constants import (
    STANCE_ATTACK,
    STANCE_BLOCK,
    STANCE_CAST,
    STANCE_COUNTER,
    STANCE_RECOVER,
    VALID_STANCES,
)
from services.battle.engine_types import ActionResult, CombatEvent, RoundContext, RoundResolution


ROUND_HANDLERS = {}


def register_handler(stance_a: str, stance_b: str):
    def decorator(func):
        ROUND_HANDLERS[(stance_a, stance_b)] = func
        return func

    return decorator


def _with_notes(text: str, area_notes: list[str], events: list[CombatEvent] | None = None) -> RoundResolution:
    return RoundResolution(text=text, area_notes=area_notes, events=events or [])


def _apply_arena(ctx: RoundContext) -> list[str]:
    area_notes = []
    if ctx.arena:
        note = ctx.arena.on_round_start(ctx.manager)
        if note:
            area_notes.append(note)
    return area_notes


def _preexisting_death_resolution(ctx: RoundContext, area_notes: list[str]) -> RoundResolution | None:
    player1 = ctx.player1
    player2 = ctx.player2
    if player1.hp <= 0 and player2.hp <= 0:
        return _with_notes(f"Both {player1.name} and {player2.name} have fallen. It's a tie!", area_notes)
    if player1.hp <= 0:
        return _with_notes(f"{player1.name} has fallen. {player2.name} wins!", area_notes)
    if player2.hp <= 0:
        return _with_notes(f"{player2.name} has fallen. {player1.name} wins!", area_notes)
    return None


def resolve_round(ctx: RoundContext) -> RoundResolution:
    area_notes = _apply_arena(ctx)
    preexisting = _preexisting_death_resolution(ctx, area_notes)
    if preexisting:
        return preexisting

    key = (ctx.player1.current_stance, ctx.player2.current_stance)
    handler = ROUND_HANDLERS.get(key)
    if handler is None:
        return _with_notes("No valid moves resolved this round.", area_notes)

    result = handler(ctx)
    return RoundResolution(
        text=result.text,
        area_notes=area_notes,
        events=result.events,
    )


@register_handler(STANCE_ATTACK, STANCE_ATTACK)
def _handle_attack_attack(ctx: RoundContext) -> RoundResolution:
    player1 = ctx.player1
    player2 = ctx.player2

    if player1.speed > player2.speed:
        p1_dmg = player1.deal_dmg(player2)
        if player2.hp <= 0:
            return RoundResolution(
                text=f"{player1.name} killed {player2.name} before they could attack",
                events=[CombatEvent("damage", "p1_first", {"amount": p1_dmg})],
            )

        p2_dmg = player2.deal_dmg(player1)
        return RoundResolution(
            text=(
                f"{player1.name} and {player2.name} both chose to attack. Since {player1.name} is faster "
                f"they went first and dealt {p1_dmg} dmg, {player2.name} responded back with {p2_dmg} dmg"
            ),
            events=[CombatEvent("exchange", "attack_attack", {"p1_dmg": p1_dmg, "p2_dmg": p2_dmg})],
        )

    if player2.speed > player1.speed:
        p2_dmg = player2.deal_dmg(player1)
        if player1.hp <= 0:
            return RoundResolution(
                text=f"{player2.name} killed {player1.name} before they could attack",
                events=[CombatEvent("damage", "p2_first", {"amount": p2_dmg})],
            )

        p1_dmg = player1.deal_dmg(player2)
        return RoundResolution(
            text=(
                f"{player1.name} and {player2.name} both chose to attack. Since {player2.name} is faster "
                f"they went first and dealt {p2_dmg} dmg, {player1.name} responded back with {p1_dmg} dmg"
            ),
            events=[CombatEvent("exchange", "attack_attack", {"p1_dmg": p1_dmg, "p2_dmg": p2_dmg})],
        )

    p1_dmg = player1.deal_dmg(player2)
    p2_dmg = player2.deal_dmg(player1)
    return RoundResolution(
        text=(
            f"coz of same speed both attacked at same time {player1.name} dealt {p1_dmg} dmg and "
            f"{player2.name} deal {p2_dmg}"
        ),
        events=[CombatEvent("exchange", "simultaneous_attack", {"p1_dmg": p1_dmg, "p2_dmg": p2_dmg})],
    )


def _build_action_result(status: str, **payload) -> ActionResult:
    return ActionResult(status=status, payload=payload)


@register_handler(STANCE_ATTACK, STANCE_BLOCK)
def _handle_attack_block(ctx: RoundContext) -> RoundResolution:
    attacker = ctx.player1
    blocker = ctx.player2
    dmg = attacker.deal_dmg(blocker)
    raw_result = blocker.block(attacker, dmg)
    block_result = _build_action_result(raw_result["status"], **{k: v for k, v in raw_result.items() if k != "status"})

    if block_result.status == "success":
        buff = block_result.payload.get("defense_buff", 0)
        reduced_dmg = int(dmg * 0.3)
        return RoundResolution(
            text=(
                f"{attacker.name} attacked, but {blocker.name} blocked most of the damage, "
                f"taking only {reduced_dmg} and gaining {buff} defense."
            ),
            events=[CombatEvent("block", "success", {"damage": reduced_dmg, "buff": buff})],
        )

    if block_result.status == "fullsuccess":
        return RoundResolution(
            text=(
                f"{blocker.name} used his hammer to block the incoming attack taking no dmg at all while gaining "
                f"{block_result.payload['defense_buff']} defense"
            ),
            events=[CombatEvent("block", "fullsuccess", block_result.payload)],
        )

    blocker.hp -= dmg
    return RoundResolution(
        text=(
            f"{blocker.name} tried to block {attacker.name}'s attack they were too slow, "
            f"taking the full {dmg} damage."
        ),
        events=[CombatEvent("block", "failed", {"damage": dmg})],
    )


@register_handler(STANCE_BLOCK, STANCE_ATTACK)
def _handle_block_attack(ctx: RoundContext) -> RoundResolution:
    player1 = ctx.player1
    player2 = ctx.player2
    dmg = player2.deal_dmg(player1)
    raw_result = player1.block(player2, dmg)
    block_result = _build_action_result(raw_result["status"], **{k: v for k, v in raw_result.items() if k != "status"})

    if block_result.status == "failed":
        player1.hp -= dmg
        return RoundResolution(
            text=f"{player1.name} tried to defend against {player2.name}'s attack but failed. Attack hit and dealt {dmg} dmg",
            events=[CombatEvent("block", "failed", {"damage": dmg})],
        )

    if block_result.status == "fullsuccess":
        return RoundResolution(
            text=(
                f"{player1.name} used his hammer to block the incoming attack taking no dmg at all while gaining "
                f"{block_result.payload['defense_buff']} defense"
            ),
            events=[CombatEvent("block", "fullsuccess", block_result.payload)],
        )

    return RoundResolution(
        text=(
            f"{player2.name} tried to attack {player1.name} but {player1.name} defended most of the dmg and "
            f"increased defense by {block_result.payload['defense_buff']} points. DMG recived {int(dmg * 0.3)}"
        ),
        events=[CombatEvent("block", "success", {"damage": int(dmg * 0.3), **block_result.payload})],
    )


@register_handler(STANCE_ATTACK, STANCE_COUNTER)
def _handle_attack_counter(ctx: RoundContext) -> RoundResolution:
    player1 = ctx.player1
    player2 = ctx.player2
    dmg = player1.deal_dmg(player2)
    counter_dmg = player2.counter(player1, dmg)
    return RoundResolution(
        text=f"{player1.name} attacked but {player2.name} countered dealing {counter_dmg} damage back.",
        events=[CombatEvent("counter", "success", {"reflected_damage": counter_dmg})],
    )


@register_handler(STANCE_COUNTER, STANCE_ATTACK)
def _handle_counter_attack(ctx: RoundContext) -> RoundResolution:
    player1 = ctx.player1
    player2 = ctx.player2
    dmg = player2.deal_dmg(player1)
    counter_dmg = player1.counter(player2, dmg)
    return RoundResolution(
        text=f"{player2.name} attacked but {player1.name} countered dealing {counter_dmg} damage back.",
        events=[CombatEvent("counter", "success", {"reflected_damage": counter_dmg})],
    )


@register_handler(STANCE_BLOCK, STANCE_BLOCK)
def _handle_block_block(ctx: RoundContext) -> RoundResolution:
    ctx.player1.hp -= 7
    ctx.player2.hp -= 7
    return RoundResolution(
        text=f"Both {ctx.player1.name} and {ctx.player2.name} chose to block. Both Lost 7 health ",
        events=[CombatEvent("block", "stalemate", {"hp_loss": 7})],
    )


@register_handler(STANCE_BLOCK, STANCE_COUNTER)
def _handle_block_counter(ctx: RoundContext) -> RoundResolution:
    ctx.player1.hp -= 2
    ctx.player2.speed -= 4
    return RoundResolution(
        text=(
            f"{ctx.player1.name} blocked while {ctx.player2.name} tried to counter. No damage dealt. "
            "Stats debuffed -2hp for p1 and -4 speed for player 2"
        ),
        events=[CombatEvent("counter", "failed", {"p1_hp_loss": 2, "p2_speed_loss": 4})],
    )


@register_handler(STANCE_COUNTER, STANCE_BLOCK)
def _handle_counter_block(ctx: RoundContext) -> RoundResolution:
    ctx.player1.speed -= 4
    ctx.player2.hp -= 2
    return RoundResolution(
        text=(
            f"{ctx.player1.name} tried to counter but {ctx.player2.name} blocked. No damage dealt. "
            "Stats lowered for both party. Loosing 4 speed and 2 hp respectively"
        ),
        events=[CombatEvent("counter", "failed", {"p1_speed_loss": 4, "p2_hp_loss": 2})],
    )


@register_handler(STANCE_COUNTER, STANCE_COUNTER)
def _handle_counter_counter(ctx: RoundContext) -> RoundResolution:
    if ctx.player1.defense >= 10:
        ctx.player1.defense -= 10
    else:
        ctx.player1.hp -= 5

    if ctx.player2.defense >= 10:
        ctx.player2.defense -= 10
    else:
        ctx.player2.hp -= 5

    return RoundResolution(
        text=f"Both {ctx.player1.name} and {ctx.player2.name} tried to counter. No damage dealt. - 10 defense for both",
        events=[CombatEvent("counter", "stalemate", {})],
    )


@register_handler(STANCE_RECOVER, STANCE_ATTACK)
def _handle_recover_attack(ctx: RoundContext) -> RoundResolution:
    dmg = ctx.player2.deal_dmg(ctx.player1)
    ctx.player1.regen(ctx.player2)
    return RoundResolution(
        text=f"{ctx.player1.name} tried to recover but was interrupted by {ctx.player2.name}'s attack dealing {dmg} damage.",
        events=[CombatEvent("recover", "interrupted", {"damage": dmg})],
    )


@register_handler(STANCE_ATTACK, STANCE_RECOVER)
def _handle_attack_recover(ctx: RoundContext) -> RoundResolution:
    ctx.player2.regen(ctx.player1)
    dmg = ctx.player1.deal_dmg(ctx.player2)
    return RoundResolution(
        text=f"{ctx.player2.name} tried to recover but was interrupted by {ctx.player1.name}'s attack dealing {dmg} damage.",
        events=[CombatEvent("recover", "interrupted", {"damage": dmg})],
    )


@register_handler(STANCE_RECOVER, STANCE_BLOCK)
def _handle_recover_block(ctx: RoundContext) -> RoundResolution:
    regen_result = ctx.player1.regen(ctx.player2)
    if regen_result["status"] == "blocked":
        block_result = ctx.player2.block(ctx.player1, 0)
        return RoundResolution(
            text=(
                f"Nuh uh {ctx.player1.name} no healing allowed this match."
                f"{ctx.player2.name} lost {block_result['defense_debuff']} defense"
            ),
            events=[CombatEvent("recover", "blocked", {"defense_debuff": block_result["defense_debuff"]})],
        )

    recovered_stat = "hp_recovered" if "hp_recovered" in regen_result else "mana_recovered"
    recovered_amount = regen_result[recovered_stat]
    block_result = ctx.player2.block(ctx.player1, 0)
    if block_result["status"] == "wrong_guess":
        return RoundResolution(
            text=(
                f"{ctx.player1.name} successfully got his {recovered_stat} by {recovered_amount} points while "
                f"{ctx.player2.name} blocked loosing {block_result['defense_debuff']} defense."
            ),
            events=[CombatEvent("recover", "success", {"recovered_stat": recovered_stat, "amount": recovered_amount})],
        )
    return RoundResolution(text="No valid moves resolved this round.")


@register_handler(STANCE_BLOCK, STANCE_RECOVER)
def _handle_block_recover(ctx: RoundContext) -> RoundResolution:
    regen_result = ctx.player2.regen(ctx.player1)
    if regen_result["status"] == "blocked":
        block_result = ctx.player1.block(ctx.player2, 0)
        return RoundResolution(
            text=(
                f"Nuh uh {ctx.player2.name} no healing allowed this match."
                f"{ctx.player1.name} lost {block_result['defense_debuff']} defense"
            ),
            events=[CombatEvent("recover", "blocked", {"defense_debuff": block_result["defense_debuff"]})],
        )

    recovered_stat = "hp_recovered" if "hp_recovered" in regen_result else "mana_recovered"
    recovered_amount = regen_result[recovered_stat]
    block_result = ctx.player1.block(ctx.player2, 0)
    if block_result["status"] == "wrong_guess":
        return RoundResolution(
            text=(
                f"{ctx.player2.name} successfully got his {recovered_stat} by {recovered_amount} points while "
                f"{ctx.player1.name} blocked loosing {block_result['defense_debuff']} defense."
            ),
            events=[CombatEvent("recover", "success", {"recovered_stat": recovered_stat, "amount": recovered_amount})],
        )
    return RoundResolution(text="No valid moves resolved this round.")


@register_handler(STANCE_RECOVER, STANCE_COUNTER)
def _handle_recover_counter(ctx: RoundContext) -> RoundResolution:
    regen_result = ctx.player1.regen(ctx.player2)
    if regen_result["status"] == "blocked":
        counter_result = ctx.player2.counter(ctx.player1, 0)
        return RoundResolution(
            text=(
                f"Nuh uh {ctx.player1.name} no healing allowed this match.\n"
                f"{ctx.player2.name} lost hp defense and speed by {counter_result['hp_drain']}, "
                f"{counter_result['defense_drain']}, {counter_result['speed_drain']}"
            ),
            events=[CombatEvent("recover", "blocked", counter_result)],
        )

    recovered_stat = "hp_recovered" if "hp_recovered" in regen_result else "mana_recovered"
    recovered_amount = regen_result[recovered_stat]
    counter_result = ctx.player2.counter(ctx.player1, 0)
    return RoundResolution(
        text=(
            f"{ctx.player1.name} successfully got their {recovered_stat} by {recovered_amount} while {ctx.player2.name} countered loosing \n"
            f"Hp - {counter_result['hp_drain']} \n"
            f"Defense - {counter_result['defense_drain']} \n"
            f"Speed - {counter_result['speed_drain']}"
        ),
        events=[CombatEvent("recover", "success", {"recovered_stat": recovered_stat, "amount": recovered_amount})],
    )


@register_handler(STANCE_COUNTER, STANCE_RECOVER)
def _handle_counter_recover(ctx: RoundContext) -> RoundResolution:
    regen_result = ctx.player2.regen(ctx.player1)
    if regen_result["status"] == "blocked":
        counter_result = ctx.player1.counter(ctx.player2, 0)
        return RoundResolution(
            text=(
                f"Nuh uh {ctx.player2.name} no healing allowed this match. {ctx.player1.name} lost hp defense and speed by "
                f"{counter_result['hp_drain']}, {counter_result['defense_drain']}, {counter_result['speed_drain']}"
            ),
            events=[CombatEvent("recover", "blocked", counter_result)],
        )

    recovered_stat = "hp_recovered" if "hp_recovered" in regen_result else "mana_recovered"
    recovered_amount = regen_result[recovered_stat]
    counter_result = ctx.player1.counter(ctx.player2, 0)
    return RoundResolution(
        text=(
            f"{ctx.player2.name} successfully got their {recovered_stat} by {recovered_amount} while {ctx.player1.name} countered loosing \n"
            f"Hp - {counter_result['hp_drain']} \n"
            f"Defense - {counter_result['defense_drain']} \n"
            f"Speed - {counter_result['speed_drain']}"
        ),
        events=[CombatEvent("recover", "success", {"recovered_stat": recovered_stat, "amount": recovered_amount})],
    )


@register_handler(STANCE_RECOVER, STANCE_RECOVER)
def _handle_recover_recover(ctx: RoundContext) -> RoundResolution:
    return RoundResolution(
        text=f"Both {ctx.player1.name} and {ctx.player2.name} tried to recover but failed",
        events=[CombatEvent("recover", "stalemate", {})],
    )


@register_handler(STANCE_CAST, STANCE_CAST)
def _handle_cast_cast(ctx: RoundContext) -> RoundResolution:
    player1 = ctx.player1
    player2 = ctx.player2

    if player1.speed == player2.speed:
        player1.mana -= 5
        player2.mana -= 5
        return RoundResolution(
            text="same speed both intrupped each others spell. unsucsseful cast drains 5 mana for each",
            events=[CombatEvent("cast", "interrupt", {"p1_mana_loss": 5, "p2_mana_loss": 5})],
        )

    if player1.speed > player2.speed:
        ok, msg = player1.cast(player2)
        if not ok:
            player1.hp -= 15
            return RoundResolution(
                text=f"{player1.name} tried casting without enough mana took drained his own life in carelessness -15 HP",
                events=[CombatEvent("cast", "backfire", {"hp_loss": 15})],
            )
        player2.mana -= 5
        return RoundResolution(
            text=(
                f"Due to higher speed {player1.name} was able to interupt {player2.name} and cast...\n "
                f"{player2.name} also lost 5 mana for failed attempt to cast \n {msg}"
            ),
            events=[CombatEvent("cast", "success", {"interrupted": player2.name})],
        )

    ok, msg = player2.cast(player1)
    if not ok:
        player2.hp -= 15
        return RoundResolution(
            text=f"{player2.name} tried casting without enough mana took drained his own life in carelessness -15 HP",
            events=[CombatEvent("cast", "backfire", {"hp_loss": 15})],
        )
    player1.mana -= 5
    return RoundResolution(
        text=(
            f"Due to higher speed {player2.name} was able to interupt {player1.name} and cast...\n "
            f"{player1.name} also lost 5 mana for failed attempt to cast \n {msg}"
        ),
        events=[CombatEvent("cast", "success", {"interrupted": player1.name})],
    )


def _handle_single_cast(caster, target) -> RoundResolution:
    ok, msg = caster.cast(target)
    if not ok:
        caster.hp -= 15
        return RoundResolution(
            text=f"{caster.name} tried casting without enough mana took drained his own life in carelessness -15 HP",
            events=[CombatEvent("cast", "backfire", {"hp_loss": 15})],
        )

    return RoundResolution(
        text=msg,
        events=[CombatEvent("cast", "success", {"caster": caster.name})],
    )


for stance in VALID_STANCES:
    if stance != STANCE_CAST:
        ROUND_HANDLERS[(STANCE_CAST, stance)] = lambda ctx, _stance=stance: _handle_single_cast(ctx.player1, ctx.player2)
        ROUND_HANDLERS[(stance, STANCE_CAST)] = lambda ctx, _stance=stance: _handle_single_cast(ctx.player2, ctx.player1)

