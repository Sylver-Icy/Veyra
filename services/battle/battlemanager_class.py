class BattleManager:
    """
    Manages the battle between two players by executing their moves each turn
    and resolving the outcomes based on their stances and stats.

    Responsibilities:
    - Set player stances and process effects each turn.
    - Resolve the round by determining damage, defense, counters, recoveries, and spell casts.
    - Determine the winner or if the battle results in a tie.
    """

    def __init__(self, player1, player2):
        self.p1 = player1
        self.p2 = player2
        self.round = 1

    def execute_turn(self, p1_move, p2_move):
        self.p1.set_stance(p1_move)
        self.p2.set_stance(p2_move)
        self.p1.proc_effect()
        self.p2.proc_effect()

    def resolve_round(self):
        player1 = self.p1
        player2 = self.p2
        self.round += 1

        # Check if players are alive before resolving moves
        if player1.hp <= 0 and player2.hp <= 0:
            return f"Both {player1.name} and {player2.name} have fallen. It's a tie!"
        elif player1.hp <= 0:
            return f"{player1.name} has fallen. {player2.name} wins!"
        elif player2.hp <= 0:
            return f"{player2.name} has fallen. {player1.name} wins!"

        # Both players choose to attack
        if player1.current_stance == 'attack' and player2.current_stance == 'attack':
            p1_dmg = player1.deal_dmg(player2)
            p2_dmg = player2.deal_dmg(player1)

            if player1.speed > player2.speed:  # p1 attacks first
                if player2.hp <= 0:
                    return (f"{player1.name} killed {player2.name} before they could attack")
                return (f"{player1.name} and {player2.name} both chose to attack. Since {player1.name} is faster "
                        f"they went first and dealt {p1_dmg} dmg, {player2.name} responded back with {p2_dmg} dmg")

            if player2.speed > player1.speed:  # p2 attacks first
                if player1.hp <= 0:
                    return (f"{player2.name} killed {player1.name} before they could attack")
                return (f"{player1.name} and {player2.name} both chose to attack. Since {player2.name} is faster "
                        f"they went first and dealt {p2_dmg} dmg, {player1.name} responded back with {p1_dmg} dmg")

            # Both players die at the same time (same speed)
            return (f"coz of same speed both attacked at same time {player1.name} dealt {p1_dmg} dmg and "
                    f"{player2.name} deal {p2_dmg}")

        # Player1 attacks, Player2 blocks
        if player1.current_stance == 'attack' and player2.current_stance == 'block':
            dmg = player1.deal_dmg(player2)
            block_result = player2.block(player1, dmg)

            if block_result['status'] == 'success':
                buff = block_result.get("defense_buff", 0)
                reduced_dmg = int(dmg * 0.3)
                return (
                    f"{player1.name} attacked, but {player2.name} blocked most of the damage, "
                    f"taking only {reduced_dmg} and gaining {buff} defense."
                )

            player2.hp -= dmg
            return (
                f"{player2.name} tried to block {player1.name}'s attack but was too slow, "
                f"taking the full {dmg} damage."
    )


        # Player1 attacks, Player2 counters
        if player1.current_stance == 'attack' and player2.current_stance == 'counter':
            dmg = player1.deal_dmg(player2)
            counter_dmg = player2.counter(player1, dmg)
            return (f"{player1.name} attacked but {player2.name} countered dealing {counter_dmg} damage back.")

        # Player1 blocks, Player2 attacks
        if player1.current_stance == 'block' and player2.current_stance == 'attack':
            dmg = player2.deal_dmg(player1)
            block_result = player1.block(player2, dmg)

            if block_result['status'] == 'failed':
                player1.hp -= dmg
                return (f"{player1.name} tried to defend against {player2.name}'s attack but failed. "
                        f"Attack hit and dealt {dmg} dmg")

            return (f"{player2.name} tried to attack {player1.name} but {player1.name} defended most of the dmg and "
                    f"increased defense by {block_result['defense_buff']} points. DMG recived {int(dmg*0.3)}")

        # Both players block
        if player1.current_stance == 'block' and player2.current_stance == 'block':
            player1.hp -= 7
            player2.hp -= 7
            return f"Both {player1.name} and {player2.name} chose to block. Both Lost 7 health "

        # Player1 blocks, Player2 counters
        if player1.current_stance == 'block' and player2.current_stance == 'counter':
            player1.hp -= 5
            player2.speed -= 4
            return f"{player1.name} blocked while {player2.name} tried to counter. No damage dealt. Stats debuffed -5hp for p1 and -4 speed for player 2"

        # Player1 counters, Player2 attacks
        if player1.current_stance == 'counter' and player2.current_stance == 'attack':
            dmg = player2.deal_dmg(player1)
            counter_dmg = player1.counter(player2, dmg)
            return f"{player2.name} attacked but {player1.name} countered dealing {counter_dmg} damage back."

        # Player1 counters, Player2 blocks
        if player1.current_stance == 'counter' and player2.current_stance == 'block':
            player1.speed -= 4
            player2.hp -=5
            return f"{player1.name} tried to counter but {player2.name} blocked. No damage dealt. Stats lowered for both party. Loosing 4 speed and 5 hp respectively"

        # Both players counter
        if player1.current_stance == 'counter' and player2.current_stance == 'counter':
            player1.defense -= 15
            player2.defense -= 15
            return f"Both {player1.name} and {player2.name} tried to counter. No damage dealt. - 15 defense for both"

        # Player1 recovers, Player2 attacks
        if player1.current_stance == 'recover' and player2.current_stance == 'attack':
            dmg = player2.deal_dmg(player1)
            return f"{player1.name} tried to recover but was interrupted by {player2.name}'s attack dealing {dmg} damage."

        # Player1 recovers, Player2 blocks
        if player1.current_stance == 'recover' and player2.current_stance == 'block':
            regen_result = player1.regen(player2)
            recovered_stat = "hp_recovered" if "hp_recovered" in regen_result else "mana_recovered"

            recovered_amount = regen_result[recovered_stat]
            block_result = player2.block(player1, 0)

            if block_result['status'] == 'failed':
                return f"{player1.name} successfully got his {recovered_stat} by {recovered_amount} points while {player2.name} blocked loosing {block_result['defense_drain']} defense and {block_result['hp_drain']} hp."

            return (
                f"{player1.name} successfully got their {recovered_stat} by {recovered_amount} points. \n"
                f"{player2.name} was too low on defense so they lost extra hp. {block_result['hp_drain']} Hp lost."
                    )

        # Player1 recovers, Player2 counters
        if player1.current_stance == 'recover' and player2.current_stance == 'counter':
            regen_result = player1.regen(player2)
            recovered_stat = "hp_recovered" if "hp_recovered" in regen_result else "mana_recovered"
            recovered_amount = regen_result[recovered_stat]

            counter_result = player2.counter(player1, 0)
            return (
                f"{player1.name} successfully got their {recovered_stat} by {recovered_amount} while {player2.name} countered loosing \n"
                f"Hp - {counter_result['hp_drain']} \n"
                f"Defense - {counter_result['defense_drain']} \n"
                f"Speed - {counter_result['speed_drain']}"
                    )


        # Player1 blocks, Player2 recover
        if player1.current_stance == 'block' and player2.current_stance == 'recover':
            regen_result = player2.regen(player1)
            recovered_stat = "hp_recovered" if "hp_recovered" in regen_result else "mana_recovered"

            recovered_amount = regen_result[recovered_stat]
            block_result = player1.block(player2, 0)

            if block_result['status'] == 'failed':
                return f"{player2.name} successfully got his {recovered_stat} by {recovered_amount} points while {player1.name} blocked loosing {block_result['defense_drain']} defense and {block_result['hp_drain']} hp."

            return (
                f"{player2.name} successfully got their {recovered_stat} by {recovered_amount} points. \n"
                f"{player1.name} was too low on defense so they lost extra hp. {block_result['hp_drain']} Hp lost."
                    )

        # Player1 attacks, Player2 recovers
        if player1.current_stance == 'attack' and player2.current_stance == 'recover':
            dmg = player1.deal_dmg(player2)
            return f"{player2.name} tried to recover but was interrupted by {player1.name}'s attack dealing {dmg} damage."

        # Player1 counters, Player2 recovers
        if player1.current_stance == 'counter' and player2.current_stance == 'recover':
            regen_result = player2.regen(player1)
            recovered_stat = "hp_recovered" if "hp_recovered" in regen_result else "mana_recovered"
            recovered_amount = regen_result[recovered_stat]

            counter_result = player1.counter(player2, 0)
            return (
                f"{player2.name} successfully got their {recovered_stat} by {recovered_amount} while {player1.name} countered loosing \n"
                f"Hp - {counter_result['hp_drain']} \n"
                f"Defense - {counter_result['defense_drain']} \n"
                f"Speed - {counter_result['speed_drain']}"
                    )

        # Both players recover
        if player1.current_stance == 'recover' and player2.current_stance == 'recover':
            return f"Both {player1.name} and {player2.name} tried to recover but failed"

        # Player1 casts a spell
        if player1.current_stance == 'cast':
            if player1.mana < 15:
                player1.hp -= 15
                return f"{player1.name} tried casting without enough mana took drained life in carelessness -15 HP"

            spell = player1.cast(player2)
            return f"{player1.name} casted a {spell} on {player2.name}"

        # Player2 casts a spell
        if player2.current_stance == 'cast':
            if player2.mana < 15:
                player2.hp -= 15
                return f"{player2.name} tried casting without enough mana took drained his own life in carelessness -15 HP"

            spell = player2.cast(player1)
            return f"{player2.name} casted a {spell} on {player1.name}"

        return "No valid moves resolved this round."
