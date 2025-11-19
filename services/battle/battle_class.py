import logging
import random

from services.battle.spell_class import Spell
from services.battle.weapon_class import Weapon

logger = logging.getLogger(__name__)


class Battle:
    """
    Represents a battle participant with stats and abilities to perform actions
    such as attack, block, counter, cast spells, and regenerate. Tracks status
    effects and current stance during battle rounds.
    """

    current_round = 0  # counter to keep track of rounds

    def __init__(self, name, spell: Spell, weapon: Weapon):
        self.attack = 5 + weapon.attack_bonus
        self.defense = 0 + weapon.defense_bonus
        self.speed = 10 + weapon.speed_bonus
        self.hp = 40 + weapon.hp_bonus
        self.mana = 10 + weapon.mana_bonus
        self.frost = 0
        self.current_stance = 'idle'
        self.status_effect = {}  # dict { "poison": 3, "nightfall": 2 }
        self.name = name
        self.spell = spell
        self.weapon = weapon
        self.can_heal = True
        self.log = []
        self.regen_state = 'hp'

    def deal_dmg(self, target: 'Battle'):
        """
        Calculate and inflict damage based on the attacker's attack stat and the
        target's defense stat. Each successful attack increases the attacker's
        attack value by 1.

        Args:
            target (Battle): The target of the attack.

        Returns:
            int: The effective damage dealt (minimum 0).
        """
        # Calculate base damage plus incremental attack bonus
        damage = self.attack + 1

        # Calculate damage reduction based on target's defense percentage
        defense = target.defense
        effective_dmg = damage - (damage * defense) // 100
        effective_dmg = max(0, effective_dmg)

        if target.current_stance not in ('block', 'counter'):
            target.hp -= effective_dmg
            result = self.weapon.on_attack_success(self, target, effective_dmg)
            self.log.append(result)

        return effective_dmg

    def block(self, target: 'Battle', dmg: int):
        """
        Attempt to block an incoming attack. Success depends on predicting an
        attack stance and speed comparison. On success, blocks 70% of damage and
        increases defense. On failure, suffers defense shred and HP drain.

        Args:
            target (Battle): The opponent attempting to attack.
            dmg (int): Incoming damage to block.

        Returns:
            Union[str, int, tuple]: 'failed' if block fails due to speed,
            defense buff amount if successful block,
            or tuple of (hp drain, defense shred) if block fails due to wrong prediction.
        """
        if target.current_stance == 'attack':
            if self.weapon.on_block(self) == "fullblock": #if the weapon returns  full block

                random_defense_buff = random.randint(12, 19)
                self.defense += random_defense_buff
                self.hp -= 0 #no hp loss
                return {
                    'status': 'fullsuccess',
                    'defense_buff': random_defense_buff
                }


            # Calculate chance to fail block based on speed difference
            fail_chance = self.calculate_fail_chance(target.speed, self.speed)
            roll = random.randint(1, 100)

            if roll <= fail_chance:
                # Block failed due to low speed
                return {
                    'status': 'failed',
                }

            # Successful block: increase defense and reduce HP damage to 30%
            random_defense_buff = random.randint(16, 29)
            self.defense += random_defense_buff
            self.hp -= int(dmg * 0.3)
            return {
                'status': 'success',
                'defense_buff': random_defense_buff
            }

        else:
            # Incorrect prediction: suffer defense and HP penalties
            random_defense_debuff = random.randint(5, 10)
            return{
                'status': 'wrong_guess',
                'defense_debuff': random_defense_debuff
            }

    def counter(self, target: 'Battle', dmg):
        """
        Attempt to counter an incoming attack. If the opponent attacked this round,
        negate all damage and reflect 50% back. If the prediction is wrong,
        suffer speed and defense debuffs or HP damage.

        Args:
            target (Battle): The opponent.
            dmg (int): Incoming damage to counter.

        Returns:
            int: Damage reflected if successful,
            or dict of (hp change, speed debuff, defense debuff) if failed.
        """
        if target.current_stance == 'attack':
            # Successful counter: reflect half the incoming damage
            dmg_reflected = int(dmg * 0.5)
            target.hp -= dmg_reflected
            return dmg_reflected

        # Failed counter: apply random speed and defense debuffs or HP damage
        random_speed_debuff = random.randint(2, 4)
        random_defense_debuff = random.randint(10, 15)
        hp_drained = 0
        if self.speed < random_speed_debuff:
            # Not enough speed to penalize attacker, take HP damage instead
            self.hp -= random_speed_debuff * 3
            hp_drained += random_defense_debuff * 3
        else:
            # Apply speed debuff
            self.speed -= random_speed_debuff

        if self.defense < random_defense_debuff:
            # Not enough defense to debuff, take HP damage instead
            self.hp -= int(random_defense_debuff * 0.5)
            hp_drained += int(random_defense_debuff * 0.5)
        else:
            # Apply defense debuff
            self.defense -= random_defense_debuff

        return {
            'hp_drain': hp_drained,
            'speed_drain': random_speed_debuff,
            'defense_drain': random_defense_debuff
        }

    def regen(self, target: 'Battle'):
        """
        Regenerate HP or mana by taking a break from battle. Can only succeed if
        opponent is defending or countering; otherwise, regeneration is interrupted.

        Args:
            target (Battle): The opponent.

        Returns:
            Union[int, str]: Amount of HP or mana regenerated, or 'intrupted' if failed.
        """


        if target.current_stance in ('block', 'counter'):
            # Choose randomly to regenerate HP or mana
            regen_stat = self.regen_state

            if regen_stat == 'hp':
                if not self.can_heal:
                    self.log.append(f"Healing is banned for entire game {self.name}")
                    self.regen_state = 'mana'
                    return {
                        'status': "blocked"
                    }

                hp_to_regen = random.randint(7, 10)
                self.hp += hp_to_regen
                self.regen_state = 'mana'

                return {
                    'status': 'success',
                    'hp_recovered': hp_to_regen
                }

            if regen_stat == 'mana':
                mana_to_regen = random.randint(3, 5)
                self.mana += mana_to_regen
                self.regen_state = 'hp'
                return {
                    'status': 'success',
                    'mana_recovered': mana_to_regen
                }
        else:
            self.regen_state = 'mana' if self.regen_state == 'hp' else 'hp'
            return {
                'status': "intrupted"
                }

    def cast(self, target: 'Battle'):
        ok, msg = self.spell.cast(self, target)
        self.weapon.on_spell_cast(self, self.spell, target, ok)
        return ok, msg


    def proc_effect(self):
        expired = []

        for effect, duration in list(self.status_effect.items()):

            if effect == "largeheal":
                if not self.can_heal:
                    self.log.append("Healing failed because of Dark blade effect")
                else:
                    self.hp += 4
                    self.log.append(f"{self.name} healed 4 hp")

            elif effect == "nightfall":
                stats = ["attack", "speed", "mana", "hp"]
                valid = [s for s in stats if getattr(self, s) > 0]
                if valid:
                    chosen = random.choice(valid)
                    new_val = max(0, getattr(self, chosen) - 2)
                    setattr(self, chosen, new_val)
                    self.log.append(f"{self.name}'s {chosen} drops by 2")

            self.status_effect[effect] -= 1
            if self.status_effect[effect] <= 0:
                expired.append(effect)

        for e in expired:
            del self.status_effect[e]
            self.log.append(f"{self.name} is no longer affected by {e}")

        #frost logic
        if self.frost >= 10:
            dmg = int(self.hp * 0.4)  # 40% of current HP
            self.hp -= dmg
            self.frost = 0
            self.log.append(f"Frostbite triggers on {self.name}, dealing {dmg} damage!")

        elif self.frost > 0:
            self.frost -= 1

        logs = self.log.copy()
        self.log.clear()
        return logs


    def set_stance(self, stance: str):
        """
        Set the current stance of the participant for the battle round.

        Args:
            stance (str): One of 'attack', 'block', 'counter', 'recover', or 'cast'.

        Returns:
            None
        """
        if stance not in ('attack', 'block', 'counter', 'recover', 'cast'):
            logger.error("Invalid stance")
            return

        self.current_stance = stance

    @staticmethod
    def calculate_fail_chance(attacker_speed, defender_speed):
        """
        Calculate the chance that a defender's action (like block) fails based on
        the speed difference between attacker and defender.

        Args:
            attacker_speed (int): Speed stat of the attacker.
            defender_speed (int): Speed stat of the defender.

        Returns:
            int: The fail chance percentage (0 if defender is faster).
        """
        if defender_speed < attacker_speed:
            speed_difference = attacker_speed - defender_speed
            fail_chance = 15 + speed_difference
            return fail_chance

        # Defender cannot fail if faster than attacker
        return 0
