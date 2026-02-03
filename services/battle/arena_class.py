

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
        return "🔥 The lava scorches you for 3 HP."


class FrozenArena(BattleArea):
    """
    Applies frost every round.
    """

    def on_round_start(self, battle_manager):
        player = battle_manager.p1
        player.frost += 1
        return "❄ Freezing wind adds 1 Frost stack."


class NullArena(BattleArea):
    """
    No environmental effects.
    Used for normal battles.
    """
    pass