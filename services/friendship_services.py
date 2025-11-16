from database.sessionmaker import Session
from models.users_model import Friendship
from services.users_services import is_user

def add_friendship(user_id: int, exp: int):
    if not is_user(user_id):
        return #no frndship if user is not registered

    with Session() as session:
        user = session.get(Friendship, user_id)

        if user:
            if user.daily_exp >= 50:
                return 0  # Daily cap reached

            user.friendship_exp += exp
            user.daily_exp += exp
            session.commit()
            return exp

        # New user entry
        new_entry = Friendship(
            user_id=user_id,
            friendship_exp=exp,
            daily_exp=exp
        )
        session.add(new_entry)
        session.commit()
        return exp

FRIENDSHIP_CHART = {
    0: "Stranger",
    100: "Acquaintance",
    300: "Casual",
    700: "Friend",
    1200: "Close Friend",
    1800: "Bestie",
    2500: "Veyra's favourite 💖"
}

def get_friendship_progress(exp: int):
    """Return current title and progress (%) to next title."""
    keys = sorted(FRIENDSHIP_CHART.keys())
    title = FRIENDSHIP_CHART[0]
    next_level = None

    for i, threshold in enumerate(keys):
        if exp >= threshold:
            title = FRIENDSHIP_CHART[threshold]
            # if not last key, next one is the next tier
            if i + 1 < len(keys):
                next_level = keys[i + 1]
        else:
            break

    # Calculate progress %
    if next_level:
        prev_level = max(k for k in keys if k <= exp)
        progress = (exp - prev_level) / (next_level - prev_level) * 100
    else:
        # at max level
        progress = 100.0

    return title, round(progress, 2)


def check_friendship(user_id: int):
    with Session() as session:
        user = session.get(Friendship, user_id)
        if user:
            exp = user.friendship_exp
            title, progress = get_friendship_progress(exp)
            return title, progress

        return FRIENDSHIP_CHART[0], 0.0

def reset_all_daily_exp():
    """Reset daily_exp for all users back to 0."""
    with Session() as session:
        session.query(Friendship).update({Friendship.daily_exp: 0})
        session.commit()