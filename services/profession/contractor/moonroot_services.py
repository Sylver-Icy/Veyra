from datetime import datetime, timezone

from sqlalchemy import false
import random


from database.sessionmaker import Session

from models.construction_model import UserTree
from models.construction_model import Sylphs

from domain.contructions.rules import get_space_required
from domain.moonroot.rules import max_sylphs_allowed, get_level_from_exp

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
            last_pruned=datetime.utcnow(),
        )

        session.add(entry)
        session.commit()

        return "Moonroot seed planted successfully! 🌱"

def get_moonroot_lvl(session, tree_id: int):
    """
    Retrieve Moonroot tree progression data.

    Args:
        session: Active database session used to query models.
        tree_id (int): ID of the Moonroot tree (UserTree primary key).

    Returns:
        tuple[int, int] | None:
            Returns (exp, lvl) if the tree exists.
            Returns None if no matching tree is found.
    """

    # Fetch the tree record by primary key
    tree = session.get(UserTree, tree_id)

    if tree:
        # Return progression-related attributes
        return tree.exp, tree.lvl

    # Tree does not exist
    return None

def can_spawn_sylph(session, tree_id: int):
    lvl_data = get_moonroot_lvl(session, tree_id)
    if not lvl_data:
        return False

    _, lvl = lvl_data
    max_allowed = max_sylphs_allowed(lvl)

    current_sylphs = session.query(Sylphs)\
    .filter(
        Sylphs.tree_id == tree_id,
        Sylphs.is_dead.is_(False)
    )\
    .count()

    return current_sylphs < max_allowed


def prune_tree(tree_id: int) -> str:
    now = datetime.utcnow()

    with Session() as session:
        tree = session.get(UserTree, tree_id)
        if not tree:
            return "The Moonroot tree seems to have vanished into thin air. 🌫️"

        if tree.last_pruned:
            hours_since_prune = (now - tree.last_pruned).total_seconds() / 3600

            if hours_since_prune < 3:
                return "You approach the Moonroot, but its branches sway smugly. Already pruned. Already thriving. 🌿"

        gained_bond = random.randint(3, 8)
        bonus_bond = 0

        if tree.last_pruned:
            hours_since_prune = (now - tree.last_pruned).total_seconds() / 3600

            if hours_since_prune >= 7:
                if random.random() <= 0.7:
                    bonus_bond = random.randint(30, 50)

        old_attunement = tree.lvl

        tree.exp += gained_bond + bonus_bond
        tree.lvl = get_level_from_exp(tree.exp)
        tree.last_pruned = now

        session.commit()

        if bonus_bond:
            msg = f"You gently prune the Moonroot. ✨ Bond deepened by {gained_bond} + BONUS {bonus_bond}."
        else:
            msg = f"You gently prune the Moonroot. ✨ Bond deepened by {gained_bond}."

        if tree.lvl > old_attunement:
            msg += " 🌳 The Moonroot hums softly. Its Attunement has grown."

        return msg