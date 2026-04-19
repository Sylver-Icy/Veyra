import random


def _process_largeheal(fighter, _effect: str, _data: dict) -> None:
    if not fighter.can_heal:
        fighter.log.append("Healing failed because of Dark blade effect")
        return

    fighter.hp += 4
    fighter.log.append(f"{fighter.name} healed 4 hp")


def _process_nightfall(fighter, _effect: str, _data: dict) -> None:
    drops = {
        "attack": 1,
        "speed": 1,
        "mana": 2,
        "hp": 3,
        "defense": 5,
    }

    valid = [stat for stat in drops if getattr(fighter, stat) > 0]
    if not valid:
        return

    chosen = random.choice(valid)
    drop = drops[chosen]
    setattr(fighter, chosen, max(0, getattr(fighter, chosen) - drop))
    fighter.log.append(f"{fighter.name}'s {chosen} drops by {drop}")


EFFECT_PROCESSORS = {
    "largeheal": _process_largeheal,
    "nightfall": _process_nightfall,
}


def process_effects(fighter) -> list[str]:
    expired = []

    for effect, data in list(fighter.status_effect.items()):
        processor = EFFECT_PROCESSORS.get(effect)
        if processor:
            processor(fighter, effect, data)

        fighter.status_effect[effect]["duration"] -= 1
        if fighter.status_effect[effect]["duration"] <= 0:
            expired.append(effect)

    for effect in expired:
        del fighter.status_effect[effect]
        fighter.log.append(f"{fighter.name} is no longer affected by {effect}")

    if fighter.frost >= 10:
        dmg = int(fighter.hp * 0.5)
        fighter.hp -= dmg
        fighter.frost = 0
        fighter.log.append(f"Frostbite triggers on {fighter.name}, dealing {dmg} damage!")
    elif fighter.frost > 0:
        fighter.frost -= 1

    logs = fighter.log.copy()
    fighter.log.clear()
    return logs

