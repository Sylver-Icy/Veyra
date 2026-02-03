

class BattleArea:
    """
    Base class for all battle arenas / environmental effects.
    Each arena can hook into different phases of a round.
    """

    def on_round_start(self, battle_manager):
        """
        Called at the very start of each round.
        Return a string message if something happens.
        """
        return None

    def on_round_end(self, battle_manager):
        """
        Called at the very end of each round.
        Return a string message if something happens.
        """
        return None


class LavaArena(BattleArea):
    """
    Constant damage over time.
    """

    def on_round_start(self, battle_manager):
        player = battle_manager.p1
        player.hp -= 3
        return "The lava scorches you for 3 HP 🔥"



class FrozenArena(BattleArea):
    """
    Applies frost every round.
    """

    def on_round_start(self, battle_manager):
        player = battle_manager.p1
        player.frost += 1
        return "❄ Freezing wind adds 1 Frost stack."


# New Arena: IrritationArena
class IrritationArena(BattleArea):
    """
    If the player uses the same stance twice in a row,
    Bardok gains +5 attack.
    """

    def on_round_start(self, battle_manager):
        player = battle_manager.p1
        enemy = battle_manager.p2

        history = list(player.move_history)

        if len(history) >= 2 and history[-1] == history[-2]:
            enemy.attack += 5
            return "Bardok grows irritated by your predictability and gains +5 Attack."

        return None


class NullArena(BattleArea):
    """
    No environmental effects.
    Used for normal battles.
    """
    pass