from database.sessionmaker import Session

from models.inventory_model import Inventory

from domain.alchemy.potion_recipes import POTION_RECIPES
from domain.alchemy.rules import can_craft_potion_tier, resolve_potion

from services.inventory_services import take_items_bulk, give_item

from utils.itemname_to_id import get_item_id_safe


def craft_potion(user_id: int, potion_name: str):
    """
    Crafts a potion:
    - fetches recipe
    - checks ingredients
    - removes required items
    - gives crafted potion
    All inside a single atomic transaction.
    """

    ok, result = resolve_potion(potion_name)
    if not ok:
        return result

    potion_key = result
    recipe = POTION_RECIPES.get(potion_key)

    ingredients = recipe["ingredients"]

    with Session() as session:
        if not can_craft_potion_tier(user_id, recipe["tier"], session):
            return f"Your Brewing stand can't make a tier {recipe['tier']} potion\n Try `!upgrade brewing stand`"

        # 1. Check ingredients
        result = check_ingredients(session, user_id, ingredients)

        if result is not True:
            return f"You are missing these items {result}"  # list of missing items or error

        # 2. Build {item_id: amount} map
        remove_map = {}

        for item_name, amount in ingredients.items():
            item_id, _ = get_item_id_safe(item_name)
            if item_id is None:
                return [f"Unknown item: {item_name}"]
            remove_map[item_id] = amount

        # 3. Remove ingredients (atomic)
        take_items_bulk(user_id, remove_map, session=session)

        # 4. Give potion
        potion_id = recipe["id"]
        if potion_id is None:
            return ["Unknown potion"]

        give_item(user_id, potion_id, 1, session=session)

        session.commit()
        return f"Successfully crafted {potion_key}"


def check_ingredients(session, user_id: int, ingredients: dict):
    """
    Checks if user has all ingredients required for a potion.
    Returns True if yes.
    Returns list of missing item names if not.
    Expects ingredients dict directly.
    """

    # Resolve ingredient names -> item IDs
    ingredient_ids = {}
    for item_name in ingredients.keys():
        item_id, _ = get_item_id_safe(item_name)
        if item_id is None:
            return [f"Unknown item: {item_name}"]
        ingredient_ids[item_id] = item_name

    rows = (
        session.query(Inventory.item_id, Inventory.item_quantity)
        .filter(
            Inventory.user_id == user_id,
            Inventory.item_id.in_(ingredient_ids.keys())
        )
        .all()
    )

    inv_map = {item_id: qty for item_id, qty in rows}

    missing = []

    for item_id, item_name in ingredient_ids.items():
        required_amount = ingredients[item_name]
        if inv_map.get(item_id, 0) < required_amount:
            missing.append(item_name)

    if missing:
        return missing

    return True