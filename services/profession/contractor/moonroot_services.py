from datetime import datetime, timezone

from database.sessionmaker import Session
from models.construction_model import UserTree
from domain.contructions.rules import get_space_required
from services.profession.land_services import allow_construction
from services.inventory_services import take_item
from utils.custom_errors import NotEnoughItemError


def plant_seed(user_id: int) -> str:
    """
    Plant a Moonroot seed if the user has space and the required item.

    Args:
        user_id (int): ID of the user planting the seed.

    Returns:
        str: Result message describing success or failure.
    """

    construction_size = get_space_required("moonroot")

    with Session() as session:
        # Check available land space
        if not allow_construction(user_id, construction_size, session):
            return "You don't have enough space on your site."

        # Attempt to consume Moonroot seed (item_id=200)
        try:
            take_item(user_id, 200, 1, session)
        except NotEnoughItemError:#THIS SHIT WONT RUN I BET 
            return "You don't have a Moonroot seed to plant."

        # Create tree entry
        entry = UserTree(
            user_id=user_id,
            last_pruned=datetime.now(timezone.utc),
        )

        session.add(entry)
        session.commit()

        return "Moonroot seed planted successfully! 🌱"