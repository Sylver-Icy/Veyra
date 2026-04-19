from services.battle.campaign.npcai import BaseAI

from services.battle.constants import (
    STANCE_ATTACK,
    STANCE_BLOCK,
    STANCE_CAST,
    STANCE_COUNTER,
    STANCE_RECOVER,
)


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

    def choose_move(self):
        weights = {
            STANCE_ATTACK: 35,
            STANCE_BLOCK: 25,
            STANCE_COUNTER: 15,
            STANCE_RECOVER: 25,
            STANCE_CAST: 0,
        }

        if self.bardok.mana >= self.bardok.spell.mana_cost:
            if any(effect in self.player.status_effect for effect in spell_effects_on_player):
                weights = {
                    STANCE_ATTACK: 35,
                    STANCE_BLOCK: 25,
                    STANCE_COUNTER: 15,
                    STANCE_RECOVER: 25,
                    STANCE_CAST: 0,
                }

            elif self.bardok.speed <= self.player.speed:
                weights[STANCE_ATTACK] = 40
                weights[STANCE_BLOCK] = 15
                weights[STANCE_CAST] = 45

            elif getattr(self.bardok.spell, "content_key", None) == "frostbite" and self.player.frost <= 5:
                weights[STANCE_ATTACK] = 40
                weights[STANCE_BLOCK] = 10
                weights[STANCE_RECOVER] = 5
                weights[STANCE_CAST] = 45

            elif getattr(self.bardok.spell, "content_key", None) == "earthquake":
                if self.player.hp <= 5:
                    return STANCE_CAST
                if self.player.defense >= 10:
                    return STANCE_CAST

                weights = {
                    STANCE_ATTACK: 35,
                    STANCE_BLOCK: 25,
                    STANCE_COUNTER: 15,
                    STANCE_RECOVER: 25,
                    STANCE_CAST: 0,
                }

            else:
                return STANCE_CAST

        elif self.stage == 13:
            history = list(self.player.move_history)

            if history:
                last_move = history[-1]
                if last_move == "attack":
                    weights[STANCE_RECOVER] += 80
                elif last_move == "recover":
                    weights[STANCE_COUNTER] += 50
                elif last_move in ("block", "counter"):
                    weights[STANCE_ATTACK] += 30

            if len(history) >= 2 and history[-1] == "attack" and history[-2] == "attack":
                weights[STANCE_ATTACK] += 60

        elif getattr(self.bardok.weapon, "content_key", None) == "moonslasher":
            weights[STANCE_ATTACK] = 60
            weights[STANCE_BLOCK] = 25
            weights[STANCE_COUNTER] = 5
            weights[STANCE_RECOVER] = 20

        elif getattr(self.bardok.weapon, "content_key", None) == "bardoksclaymore":
            weights[STANCE_ATTACK] = 60
            weights[STANCE_BLOCK] = 20
            weights[STANCE_COUNTER] = 10
            weights[STANCE_RECOVER] = 10

        elif self.player.hp < 10:
            weights[STANCE_ATTACK] = 50
            weights[STANCE_BLOCK] = 30
            weights[STANCE_COUNTER] = 10
            weights[STANCE_RECOVER] = 10

        elif self.bardok.hp < 10:
            weights[STANCE_ATTACK] = 40
            weights[STANCE_BLOCK] = 15
            weights[STANCE_COUNTER] = 30
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
