from services.battle.campaign.npcai import BaseAI

from services.battle.weapon_class import BardoksClaymore, MoonSlasher
from services.battle.spell_class import Earthquake, FrostBite


spell_effects_on_player = ["nightfall"]
class BardokAI(BaseAI):
    """
    Aggressive, pressure-focused AI.
    Designed to punish repetition and favor direct combat.
    """

    def __init__(self, bardok=None, player=None, stage=11):
        super().__init__(fighter=bardok, opponent=player)
        self.bardok = bardok
        self.player = player
        self.stage = stage
        self.bardok.origin = "bardok"
        self.attack_weight = 0
        self.block_weight = 0
        self.counter_weight = 0
        self.recover_weight = 0
        self.cast_weight = 0

    def choose_move(self):
        # --- BASELINE (ALWAYS NON-ZERO) ---
        self.attack_weight = 35
        self.block_weight = 25
        self.counter_weight = 15
        self.recover_weight = 25
        self.cast_weight = 0

        # --- SPELL PRIORITY ---
        if self.bardok.mana >= self.bardok.spell.mana_cost:
            if any(effect in self.player.status_effect for effect in spell_effects_on_player):
                self.attack_weight = 35
                self.block_weight = 25
                self.counter_weight = 15
                self.recover_weight = 25

            elif self.bardok.speed <= self.player.speed:
                self.attack_weight = 40
                self.block_weight = 15
                self.cast_weight = 45

            elif isinstance(self.bardok.spell, FrostBite) and self.player.frost <= 5:
                self.attack_weight = 40
                self.block_weight = 10
                self.recover_weight = 5
                self.cast_weight = 45

            elif isinstance(self.bardok.spell, Earthquake):
                if self.player.hp <=5:
                    return "cast"
                if self.player.defense >= 10:
                    return "cast"

                self.attack_weight = 35
                self.block_weight = 25
                self.counter_weight = 15
                self.recover_weight = 25

            else:
                return "cast"

        elif self.stage == 13:
            # Player cannot repeat moves -> anticipate forced rotation
            history = list(self.player.move_history)

            if history:
                last_move = history[-1]

                # If player attacked last round -> likely forced to recover
                if last_move == "attack":
                    self.recover_weight += 80

                # If player recovered last round -> likely forced to counter
                elif last_move == "recover":
                    self.counter_weight += 50

                # If player blocked or countered last round -> likely forced to attack
                elif last_move in ("block", "counter"):
                    self.attack_weight += 30

            # HARD PUNISH: if player same stance twice in a row
            if len(history) >= 2 and history[-1] == "attack" and history[-2] == "attack":
                self.attack_weight += 60

        # --- WEAPON-BASED BEHAVIOR ---
        elif isinstance(self.bardok.weapon, MoonSlasher):
            self.attack_weight = 60
            self.block_weight = 25
            self.counter_weight = 5
            self.recover_weight = 20

        elif isinstance(self.bardok.weapon, BardoksClaymore):
            self.attack_weight = 60
            self.block_weight = 20
            self.counter_weight = 10
            self.recover_weight = 10

        # --- HP / STATE-BASED FALLBACKS ---
        elif self.player.hp < 10:
            self.attack_weight = 50
            self.block_weight = 30
            self.counter_weight = 10
            self.recover_weight = 10

        elif self.bardok.hp < 10:
            self.attack_weight = 40
            self.block_weight = 15
            self.counter_weight = 30
            self.recover_weight = 15

        # --- PLAYER PATTERN BIAS (SPRINKLES ONLY) ---
        history = list(self.player.move_history)

        if history:
            attack_rate = history.count("attack") / len(history)
            block_rate = history.count("block") / len(history)
            counter_rate = history.count("counter") / len(history)

            if attack_rate > 0.6:
                self.counter_weight += 20
                self.block_weight += 10
                self.recover_weight -= 10

            if block_rate > 0.5:
                self.recover_weight += 15

            if counter_rate > 0.5:
                self.attack_weight -= 15
                self.recover_weight += 20

        # --- IF ALL FAILS GACHA GO BRRRRR ---
        else:
            self.attack_weight = 25
            self.block_weight = 25
            self.counter_weight = 25
            self.recover_weight = 25

        # --- FINAL DECISION ---
        return self.weighted_choice([
            self.attack_weight,
            self.block_weight,
            self.counter_weight,
            self.recover_weight,
            self.cast_weight
        ])