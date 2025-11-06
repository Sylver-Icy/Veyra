import logging
import random

logger = logging.getLogger(__name__)


class Battle:
    """
    Represents a battle participant with stats and abilities to perform actions
    such as attack, block, counter, cast spells, and regenerate. Tracks status
    effects and current stance during battle rounds.
    """

    current_round = 0  # counter to keep track of rounds

    def __init__(self, name):
        self.attack = 10
        self.defense = 10
        self.speed = 10
        self.hp = 50
        self.mana = 12
        self.current_stance = 'idle'
        self.status_effect = 'none'
        self.name = name

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

        # Inflict damage only if target is not blocking or countering
        if target.current_stance not in ('block', 'counter'):
            target.hp -= effective_dmg
            self.attack += 1  # increase attack strength after successful hit

        return max(0, effective_dmg)

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
            regen_stat = random.choice(['hp', 'mana'])

            if regen_stat == 'hp':
                hp_to_regen = random.randint(7, 10)
                self.hp += hp_to_regen
                return {
                    'status': 'success',
                    'hp_recovered': hp_to_regen
                }

            if regen_stat == 'mana':
                mana_to_regen = random.randint(3, 5)
                self.mana += mana_to_regen
                return {
                    'status': 'success',
                    'mana_recovered': mana_to_regen
                }
        else:
            return {
                'status': "intrupted"
                }

    def cast(self, target: 'Battle'):
        """
        Cast a spell chosen randomly from a predefined list if enough mana is available.
        Spells include fireball, poison, nightfall, and heavyshot, each with unique effects.

        Args:
            target (Battle): The target of the spell.

        Returns:
            Union[str, None]: The name of the spell cast, or None if not enough mana.
        """
        if self.mana < 15:
            return

        spell = random.choice(['fireball', 'poison', 'nightfall', 'heavyshot'])
        self.mana -= 15

        if spell == 'fireball':
            # Deals fixed 24 damage
            target.hp -= 24
            return 'fireball'

        elif spell == 'poison':
            # Applies poison status effect
            target.status_effect = 'poisoned'
            return 'poisoned'

        elif spell == 'nightfall':
            # Applies nightfall status effect
            target.status_effect = 'nightfall'
            return 'nightfall'

        else:
            # Sets target's HP equal to caster's HP
            target.hp = self.hp
            return 'heavyshot'

    def proc_effect(self):
        """
        Process the current status effect on this participant, applying its effects.

        Returns:
            Union[int, tuple, None]: Updated HP if poisoned,
            or tuple of (stat affected, new value) if nightfall effect applied,
            or None if no effect.
        """
        effect = self.status_effect

        if effect == 'poisoned':
            # Poison effect reduces HP by 4 each turn
            self.hp -= 4
            return self.hp

        elif effect == 'nightfall':
            # Nightfall randomly reduces one stat by 2, but only if it's above 0
            possible_stats = [stat for stat in ['attack', 'speed', 'mana', 'hp'] if getattr(self, stat) > 0]

            if not possible_stats:
                # all stats are already at zero, no effect
                return None

            stat_affected = random.choice(possible_stats)
            current_value = getattr(self, stat_affected)
            new_value = max(0, current_value - 2)
            setattr(self, stat_affected, new_value)
            return (stat_affected, new_value)


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
        else:
            # Defender cannot fail if faster than attacker
            return 0
