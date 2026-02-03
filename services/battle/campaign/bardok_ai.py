from services.battle.campaign.npcai import BaseAI


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
        self.origin = "bardok"

    def choose_move(self):
        attack = 40
        block = 35
        counter = 10
        recover = 15
        cast = 0


        # If player is low HP -> finish them
        if self.player.hp <= 25:
            attack += 20

        # If Bardok is low HP -> slight defensive bias
        if self.bardok.hp <= 25:
            block += 10
            counter += 10

        # Punish repeated player stances
        history = list(self.player.move_history)
        if len(history) >= 2 and history[-1] == history[-2]:
            counter += 25
            attack += 10

        # Stage-based tuning

        if self.stage >= 14:
            attack += 15

        return self.weighted_choice([
            attack,
            block,
            counter,
            recover,
            cast
        ])