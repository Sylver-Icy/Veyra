from services.battle.constants import (
    STANCE_ATTACK,
    STANCE_BLOCK,
    STANCE_CAST,
    STANCE_COUNTER,
    STANCE_RECOVER,
)
from services.battle.campaign.npcai import BaseAI

spell_effects_on_player = ["nightfall"]
spell_effects_on_veyra = ["veilofdarkness"]


class VeyraAI(BaseAI):
    def __init__(self, difficulty="normal", veyra=None, player=None):
        super().__init__(fighter=veyra, opponent=player)
        self.difficulty = difficulty
        self.veyra = veyra
        self.player = player

    def choose_move(self):
        weights = {
            STANCE_ATTACK: 25,
            STANCE_BLOCK: 25,
            STANCE_COUNTER: 25,
            STANCE_RECOVER: 25,
            STANCE_CAST: 0,
        }

        if self.veyra.mana >= self.veyra.spell.mana_cost:
            if any(effect in self.player.status_effect for effect in spell_effects_on_player):
                weights[STANCE_ATTACK] = 40
                weights[STANCE_BLOCK] = 15
                weights[STANCE_COUNTER] = 30
                weights[STANCE_RECOVER] = 15

            if any(effect in self.veyra.status_effect for effect in spell_effects_on_veyra):
                weights[STANCE_ATTACK] = 40
                weights[STANCE_BLOCK] = 15
                weights[STANCE_COUNTER] = 30
                weights[STANCE_RECOVER] = 15

            elif self.veyra.speed <= self.player.speed:
                weights[STANCE_ATTACK] = 40
                weights[STANCE_BLOCK] = 15
                weights[STANCE_CAST] = 45

            elif getattr(self.veyra.spell, "content_key", None) == "frostbite" and self.player.frost <= 5:
                weights[STANCE_ATTACK] = 40
                weights[STANCE_BLOCK] = 5
                weights[STANCE_CAST] = 55
            else:
                return STANCE_CAST

        elif getattr(self.veyra.weapon, "content_key", None) == "moonslasher":
            weights[STANCE_ATTACK] = 70
            weights[STANCE_BLOCK] = 25
            weights[STANCE_COUNTER] = 5
            weights[STANCE_RECOVER] = 10

        elif getattr(self.veyra.weapon, "content_key", None) == "elephanthammer":
            weights[STANCE_ATTACK] = 40
            weights[STANCE_BLOCK] = 40
            weights[STANCE_COUNTER] = 0
            weights[STANCE_RECOVER] = 20

        elif self.player.hp < 20:
            weights[STANCE_ATTACK] = 40
            weights[STANCE_BLOCK] = 30
            weights[STANCE_COUNTER] = 20
            weights[STANCE_RECOVER] = 10

        elif self.veyra.hp < 20:
            weights[STANCE_ATTACK] = 40
            weights[STANCE_BLOCK] = 35
            weights[STANCE_COUNTER] = 10
            weights[STANCE_RECOVER] = 15

        history = list(self.player.move_history)

        if history:
            attack_rate = history.count("attack") / len(history)
            block_rate = history.count("block") / len(history)
            counter_rate = history.count("counter") / len(history)

            if attack_rate > 0.6:
                weights[STANCE_COUNTER] += 20
                weights[STANCE_BLOCK] += 10
                weights[STANCE_RECOVER] -= 10

            if block_rate > 0.5:
                weights[STANCE_RECOVER] += 15

            if counter_rate > 0.5:
                weights[STANCE_ATTACK] -= 15
                weights[STANCE_RECOVER] += 20

        else:
            weights = {
                STANCE_ATTACK: 25,
                STANCE_BLOCK: 25,
                STANCE_COUNTER: 25,
                STANCE_RECOVER: 25,
                STANCE_CAST: weights[STANCE_CAST],
            }

        return self.weighted_choice([
            weights[STANCE_ATTACK],
            weights[STANCE_BLOCK],
            weights[STANCE_COUNTER],
            weights[STANCE_RECOVER],
            weights[STANCE_CAST],
        ])
