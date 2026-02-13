from database.sessionmaker import Session

from models.construction_model import Sylphs

from services.profession.contractor.moonroot_services import can_spawn_sylph

from utils.create_name import create_sylph_name

def spawn_sylph(user_id: int, tree_id: int, name: str = None):
    """
    Spawn a new Sylph linked to a Moonroot tree.

    If no name is provided, a procedural Sylph name is generated.
    The function validates whether the tree is eligible to spawn
    a Sylph before creating the record.

    Args:
        user_id (int): ID of the user owning the Sylph.
        tree_id (int): ID of the Moonroot tree associated with the Sylph.
        name (str, optional): Custom Sylph name. If omitted, one is generated.

    Returns:
        Sylphs | None:
            Returns the created Sylph object on success.
            Returns None if spawning is not allowed.
    """

    # Generate a name if none was supplied
    if not name:
        name = create_sylph_name()

    with Session() as session:
        # Validate spawning conditions (tree level, limits, etc.)
        if not can_spawn_sylph(session, tree_id):
            return None

        # Create Sylph database record
        new_sylph = Sylphs(
            user_id=user_id,
            tree_id=tree_id,
            name=name
        )

        session.add(new_sylph)
        session.commit()

        # Return the persisted Sylph instance
        return new_sylph.name
