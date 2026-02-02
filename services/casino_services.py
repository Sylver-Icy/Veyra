from domain.casino.games import GAMES

from database.sessionmaker import Session

from services.economy_services import remove_chips, add_chip, check_wallet_full

from utils.custom_errors import VeyraError
from utils.emotes import CHIP_EMOJI


def play_casino_game(user_id: int, game_id: str, bet: int, choice: str):
    game = GAMES.get(game_id)
    if not game:
        return "Invalid game."

    # bet validation
    if bet < game.min_bet:
        return f"Min bet is {game.min_bet} chips. Come onnnnn BET BIG TO WIN BIG."
    if bet > game.max_bet:
        return f"Max bet is {game.max_bet} chips. Since I'd not be issuing refund coz someone lost entire entire net worth in a single gamble."


    with Session() as session:
        gold, chips = check_wallet_full(user_id, session)

        if chips < bet:
            return f"You have {chips}{CHIP_EMOJI} and you need at least {bet} chips to cover possible losses. You can buy more chips from `/casino`"

        try:
            result = game.play(bet, choice)

            # Check for GAMBLER'S FATE effect
            from services.alchemy_services import get_active_user_effect, expire_user_effect

            active_effect = get_active_user_effect(session, user_id)

            if result.delta < 0:
                loss = -result.delta

                # If Gambler's Fate active -> only deduct 90% and remove effect
                if active_effect == "GAMBLER'S FATE":
                    reduced_loss = int(loss * 0.9)
                    remove_chips(user_id, reduced_loss, session)
                    expire_user_effect(session, user_id, "GAMBLER'S FATE")
                    session.commit()
                    return f"{result.message}\nYour chips were partially refunded by **GAMBLER'S FATE**. The aura fades away."

                remove_chips(user_id, loss, session)

            elif result.delta > 0:
                add_chip(user_id, result.delta, session)

            session.commit()
            return result.message

        except VeyraError:
            session.rollback()
            return "Some crazy error happened 😵‍💫 Your bet was refunded dw"
        except Exception:
            session.rollback()
            raise