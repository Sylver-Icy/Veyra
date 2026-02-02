import random
from collections import deque

from services.battle.weapon_class import ElephantHammer, MoonSlasher
from services.battle.spell_class import FrostBite

spell_effects_on_player = ["nightfall"]
spell_effects_on_veyra = ["veilofdarkness"]
class VeyraAI:
    def __init__(self, difficulty="normal", veyra = None, player = None):
        self.difficulty = difficulty
        self.veyra = veyra
        self.player = player
        if not hasattr(self.player, "move_history"):
            self.player.move_history = deque(maxlen=5)
        self.attack_weight = 0
        self.block_weight = 0
        self.counter_weight = 0
        self.recover_weight = 0
        self.cast_weight = 0

    def choose_move(self):
         # --- BASELINE (ALWAYS NON-ZERO) ---
        self.attack_weight = 25
        self.block_weight = 25
        self.counter_weight = 25
        self.recover_weight = 25
        self.cast_weight = 0

        # --- SPELL PRIORITY ---
        if self.veyra.mana >= self.veyra.spell.mana_cost:
            if any(effect in self.player.status_effect for effect in spell_effects_on_player):
                self.attack_weight = 40
                self.block_weight = 15
                self.counter_weight = 30
                self.recover_weight = 15

            if any(effect in self.veyra.status_effect for effect in spell_effects_on_veyra):
                self.attack_weight = 40
                self.block_weight = 15
                self.counter_weight = 30
                self.recover_weight = 15

            elif self.player.frost <= 5:
                self.attack_weight = 40
                self.block_weight = 5
                self.cast_weight = 55
            else:
                return "cast"

        # --- WEAPON-BASED BEHAVIOR ---
        elif isinstance(self.veyra.weapon, MoonSlasher):
            self.attack_weight = 70
            self.block_weight = 25
            self.counter_weight = 5
            self.recover_weight = 10

        elif isinstance(self.veyra.weapon, ElephantHammer):
            self.attack_weight = 40
            self.block_weight = 40
            self.counter_weight = 0
            self.recover_weight = 20

        # --- HP / STATE-BASED FALLBACKS ---
        elif self.player.hp < 20:
            self.attack_weight = 40
            self.block_weight = 30
            self.counter_weight = 20
            self.recover_weight = 10

        elif self.veyra.hp < 20:
            self.attack_weight = 40
            self.block_weight = 35
            self.counter_weight = 10
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
        return random.choices(
            ["attack", "block", "counter", "recover", "cast"],
            weights=[
                self.attack_weight,
                self.block_weight,
                self.counter_weight,
                self.recover_weight,
                self.cast_weight
            ]
        )[0]