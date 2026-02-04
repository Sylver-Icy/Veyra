class Weapon():
    def __init__(self,name, attack_bonus=0, hp_bonus=0, defense_bonus=0, speed_bonus=0, mana_bonus=0):
        self.name = name
        self.attack_bonus = attack_bonus
        self.defense_bonus = defense_bonus
        self.hp_bonus = hp_bonus
        self.speed_bonus = speed_bonus
        self.mana_bonus = mana_bonus

    # hooks ↓
    def on_attack_success(self, attacker, defender, damage): pass
    def on_attack_fail(self, attacker, defender): pass
    def on_receive_attack(self, defender, attacker, damage): pass
    def on_spell_cast(self, caster, spell, target, result): pass
    def on_regen(self, player): pass
    def on_block(self, defender): pass
    def on_turn_start(self, player): pass
    def on_turn_end(self, player): pass


class TrainingBlade(Weapon):
    def __init__(self, name = "Training Blade", attack_bonus=5):
        super().__init__(name, attack_bonus=attack_bonus)

    def on_attack_success(self, attacker, defender, damage):
        attacker.attack += 1
        return f"Training Blade passive: {attacker.name}'s attack increased by 1"

class MoonSlasher(Weapon):
    def __init__(self, name = "The Moon Slasher", attack_bonus=2, hp_bonus=5, defense_bonus=8, speed_bonus=3, mana_bonus=1):
        super().__init__(name, attack_bonus=attack_bonus, hp_bonus=hp_bonus, defense_bonus=defense_bonus, speed_bonus=speed_bonus, mana_bonus=mana_bonus)

    def on_attack_success(self, attacker, defender, damage):
        defender.frost += 4
        return f"The Moon Slasher passive: {defender.name} started feeling chills.. Frost building up!"

class EternalTome(Weapon):
    def __init__(self, name = "Eternal Tome", attack_bonus=3, mana_bonus=5):
        super().__init__(name, attack_bonus=attack_bonus, mana_bonus=mana_bonus)

    def on_spell_cast(self, caster, spell, target, result):
        if not result:
            return None

        extended = False

        effect_containers = []

        if hasattr(target, "status_effect") and target.status_effect:
            effect_containers.append(target.status_effect)

        if target != caster and hasattr(caster, "status_effect") and caster.status_effect:
            effect_containers.append(caster.status_effect)

        for container in effect_containers:
            for eff, data in container.items():
                if data.get("source") == caster:
                    data["duration"] += 3
                    extended = True

        if extended:
            return "Eternal Tome passive: Your spell effects last longer!"
        return None

class ElephantHammer(Weapon):
    def __init__(self, name = "Elephant Hammer", attack_bonus=3, hp_bonus=10, defense_bonus=15, speed_bonus=-1):
        super().__init__(name, attack_bonus=attack_bonus, hp_bonus=hp_bonus, defense_bonus=defense_bonus, speed_bonus=speed_bonus)

    def on_block(self, defender):
        return "fullblock"

class DarkBlade(Weapon):
    def __init__(self, name = "Dark Blade", attack_bonus=8):
        super().__init__(name, attack_bonus=attack_bonus)

    def on_attack_success(self, attacker, defender, damage):
        defender.can_heal = False
        attacker.can_heal = False
        return "DarkBlade effect: Neither party can heal for rest of the game"

class VeyrasGrimoire(Weapon):
    def __init__(self, name = "VeyrasGrimoire", attack_bonus=2, mana_bonus=2):
        super().__init__(name, attack_bonus=attack_bonus, mana_bonus=mana_bonus)

    def on_spell_cast(self, caster, spell, target, result):
        if not result:
            return None

        caster.hp -= 5
        caster.mana += 4
        return "Veyra's Grimoire passive: +4 mana, -5 HP"

class BardoksClaymore(Weapon):
    def __init__(self, name="Bardok's Claymore", attack_bonus=10, defense_bonus=-10, speed_bonus=-2):
        super().__init__(
            name,
            attack_bonus=attack_bonus,
            defense_bonus=defense_bonus,
            speed_bonus=speed_bonus
        )

    def on_attack_success(self, attacker, defender, damage):
        if attacker.origin == "bardok":
            attacker.hp += 4
            return "Bardok's Claymore passive: Bardok siphons vitality and heals 4 HP"
        return "Bardok's Claymore trembles in your hands... it refuses to awaken."
