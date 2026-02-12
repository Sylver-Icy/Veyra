from models.users_model import UserLand


def allow_construction(user_id: int, construction_size: int, session) -> bool:
    """
    Determine whether a user has enough free land to construct something.

    Args:
        user_id (int): The ID of the user whose land is being checked.
        construction_size (int): The amount of land required.
        session: Database session used to fetch UserLand.

    Returns:
        bool: True if the user has sufficient available land, False otherwise.
    """

    # Fetch the user's land record
    user = session.get(UserLand, user_id)
    #TEMPORARY REMOVE IT LATER BITCH
    if not user:
        give_land(user_id, 100, session)
        user = session.get(UserLand, user_id)

    # Calculate remaining usable land
    available_land = user.land_owned - user.land_used

    # Check if construction can proceed
    return available_land >= construction_size


def give_land(user_id: int, amount: int, session) -> None:
    """
    Add land to a user. Creates a land record if missing.

    Args:
        user_id (int): The ID of the user receiving land.
        amount (int): Amount of land to add.
        session: Database session used to fetch/update UserLand.
    """

    land = session.get(UserLand, user_id)

    if land is None:
        land = UserLand(user_id=user_id, land_owned=amount, land_used=0)
        session.add(land)
    else:
        land.land_owned += amount

