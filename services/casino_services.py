"""
Casino service logic for handling casino game plays.

Responsibilities:
- Validate game and bet inputs
- Check user wallet state
- Apply game results (win/loss)
- Handle special effects like GAMBLER'S FATE
- Ensure DB consistency with proper commit/rollback
"""

from domain.casino.games import GAMES
from database.sessionmaker import Session
from services.economy_services import (
    remove_chips,
    add_chip,
    check_wallet_full,
)
from services.alchemy_services import (
    get_active_user_effect,
    expire_user_effect,
)
from utils.custom_errors import VeyraError
from utils.emotes import CHIP_EMOJI


def play_casino_game(user_id: int, game_id: str, bet: int, choice: str) -> dict:
    """
    Plays a casino game for a user.

    Args:
        user_id (int): Discord/user ID
        game_id (str): Casino game identifier
        bet (int): Amount of chips wagered
        choice (str): Player's game-specific choice

    Returns:
        dict: Result message to display to the user
    """
    game = GAMES.get(game_id)
    if not game:
        return {"game": "error", "summary": "That game doesn't exist. Even the casino is confused."}

    # ---- Bet validation ----
    if bet < game.min_bet:
        return {
            "game": "error",
            "summary": f"Minimum bet is **{game.min_bet}**{CHIP_EMOJI}. COME ON!! Bet Big to WIN BIG!"
        }

    if bet > game.max_bet:
        return {
            "game": "error",
            "summary": f"Maximum bet is **{game.max_bet}**{CHIP_EMOJI}. We're reckless, not irresponsible."
        }

    with Session() as session:
        _, chips = check_wallet_full(user_id, session)

        if chips < bet:
            return {
                "game": "error",
                "summary": f"You have **{chips}**{CHIP_EMOJI} but tried to bet **{bet}**. Bold move. Unfortunately, math exists."
            }

        try:
            # Play the game (pure logic, no DB side effects inside)
            result = game.play(bet, choice)

            active_effect = get_active_user_effect(session, user_id)

            # ---- Loss handling ----
            if result.delta < 0:
                loss = -result.delta

                # GAMBLER'S FATE reduces loss once, then expires
                if active_effect == "GAMBLER'S FATE":
                    reduced_loss = int(loss * 0.9)
                    remove_chips(user_id, reduced_loss, session)
                    expire_user_effect(session, user_id, "GAMBLER'S FATE")
                    session.commit()

                    return {
                        "game": game_id,
                        "summary": (
                            f"{result.message}\n"
                            "**GAMBLER'S FATE** cushions the blow. Your chips were partially refunded"
                        ),
                        "delta": -reduced_loss,
                        "won": False,
                        **result.meta
                    }

                remove_chips(user_id, loss, session)

            # ---- Win handling ----
            elif result.delta > 0:
                add_chip(user_id, result.delta, session)

            session.commit()
            return {
                "game": game_id,
                "summary": result.message,
                "delta": result.delta,
                "won": result.delta > 0,
                **result.meta
            }

        except VeyraError:
            session.rollback()
            return {
                "game": "error",
                "summary": "Something went off the rails mid-spin 😵‍💫\nYour bet is safe. The casino pretends this never happened."
            }

        except Exception:
            session.rollback()
            raise
