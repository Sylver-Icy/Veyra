from datetime import datetime, timedelta

from database.sessionmaker import Session

from models.inventory_model import Inventory
from models.users_model import UserEffects

from domain.alchemy.potion_recipes import POTION_RECIPES
from domain.alchemy.rules import can_craft_potion_tier, resolve_potion, roll_strain_risk

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


def apply_user_effect(session, user_id: int, effect_name: str, strain: int, expire_hours=None):
    """
    Applies or updates a user effect.
    - Strain is ALWAYS added
    - Effect name is overwritten
    - Only one effect row per user
    - expire_hours: number of hours from now the effect should last
    """

    # Convert hours -> timestamp
    expire_at = None
    if expire_hours is not None:
        expire_at = datetime.utcnow() + timedelta(hours=expire_hours)

    existing = (
        session.query(UserEffects)
        .filter(UserEffects.user_id == user_id)
        .first()
    )

    if existing:
        existing.strain += strain
        existing.effect_name = effect_name
        existing.expire_at = expire_at
    else:
        new_effect = UserEffects(
            user_id=user_id,
            effect_name=effect_name,
            strain=strain,
            expire_at=expire_at
        )
        session.add(new_effect)

    return True


def reduce_user_strain(session, user_id: int, amount: int):
    effect = (
        session.query(UserEffects)
        .filter(UserEffects.user_id == user_id)
        .first()
    )

    if not effect:
        return False

    effect.strain -= amount

    if effect.strain < 0:
        effect.strain = 0

    session.commit()
    return True

def get_strain_status(session, user_id: int):
    """
    Returns a descriptive sentence about the user's current strain level.
    """

    effect = (
        session.query(UserEffects)
        .filter(UserEffects.user_id == user_id)
        .first()
    )

    if not effect or effect.strain <= 0:
        return "Your body feels normal. No lingering side effects remain."

    strain = effect.strain

    if 0 < strain <= 10:
        return "You feel mostly fine. A slight dizziness lingers, but another potion should be safe."

    if 11 <= strain <= 30:
        return "Your head feels light and your body is warm. Drinking more might start to feel uncomfortable."

    if 31 <= strain <= 60:
        return "Your stomach churns and your vision blurs slightly. Another potion could make things worse."

    if 61 <= strain <= 89:
        return "You feel nauseous, weak, and unsteady. Drinking another potion is risky."

    return "You are extremely sick. Your body is rejecting the toxins. Drinking another potion could make you faint."


# New function: use_potion
def use_potion(user_id: int, potion_name: str):
    """
    Uses a potion:
    - Resolves potion
    - Fetches effect + strain from recipe
    - Rolls strain risk
    - Applies effect if successful
    """

    ok, result = resolve_potion(potion_name)
    if not ok:
        return result

    potion_key = result
    recipe = POTION_RECIPES.get(potion_key)

    effect_name = recipe.get("effect")
    strain_amount = recipe.get("strain")

    if effect_name is None or strain_amount is None:
        return "This potion has no effect."

    with Session() as session:
        # Get current strain
        effect_row = (
            session.query(UserEffects)
            .filter(UserEffects.user_id == user_id)
            .first()
        )

        current_strain = effect_row.strain if effect_row else 0

        # Roll risk
        if not roll_strain_risk(current_strain):
            return "You attempt to drink the potion, but your body violently rejects it. You collapse to the ground as darkness takes you. The potion is wasted."

        # Apply effect
        apply_user_effect(
            session=session,
            user_id=user_id,
            effect_name=effect_name,
            strain=strain_amount,
            expire_hours=recipe.get("expire_at")
        )

        session.commit()
        return f"You drink the potion and feel its effects: {effect_name}"


def get_active_user_effect(session, user_id: int):
    """
    Returns active effect name.
    If expired or missing -> None.
    """
    effect = (
        session.query(UserEffects)
        .filter(UserEffects.user_id == user_id)
        .first()
    )

    if not effect:
        return None

    if effect.expire_at is not None and effect.expire_at <= datetime.utcnow():
        return None

    return effect.effect_name



def expire_user_effect(session, user_id: int, effect_name: str | None = None):
    """
    Forces the user's current effect to expire by setting expire_at to a past timestamp.
    """

    effect = (
        session.query(UserEffects)
        .filter(UserEffects.user_id == user_id)
        .first()
    )

    if not effect:
        return False

    # If a specific effect name is provided and it doesn't match -> do nothing
    if effect_name is not None and effect.effect_name != effect_name:
        return False

    effect.expire_at = datetime.utcnow() - timedelta(seconds=1)
    session.commit()
    return True