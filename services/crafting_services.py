from services.inventory_services import give_item, take_items_bulk

from domain.crafting.rules import validate_smelt_amount, get_required_ore, required_ore_amount
from domain.shared.errors import InvalidAmountError, InvalidRecipeError

from utils.itemname_to_id import get_item_id_safe
from utils.custom_errors import NotEnoughItemError, FullInventoryError, PartialInventoryError

from database.sessionmaker import Session


def smelt(user_id: int, bar_name: str, amount: int, coal_cost: int):
    bar_name = bar_name.lower()

    try:
        amount = validate_smelt_amount(amount)
    except InvalidAmountError:
        return "Smelt amount must be positive."

    try:
        ore_name = get_required_ore(bar_name)
    except InvalidRecipeError:
        return f"'{bar_name}' is not a valid bar to smelt."

    ore_id, _ = get_item_id_safe(ore_name)
    bar_id, _ = get_item_id_safe(bar_name)
    coal_id, _ = get_item_id_safe("coal")

    ore_needed = required_ore_amount(amount)

    with Session() as session:
        try:
            take_items_bulk(user_id, {
                ore_id: ore_needed,
                coal_id: amount * coal_cost
            }, session=session)

            give_item(user_id, bar_id, amount, session=session)

            session.commit()

        except NotEnoughItemError:
            session.rollback()
            return "Not enough materials to smelt."

        except (FullInventoryError, PartialInventoryError):
            session.rollback()
            return "No Space in inventory to craft this! Either free up or upgrade via `!upgrade inventory`"

        except Exception:
            session.rollback()
            raise

    return f"🔥 Successfully smelted {amount}x {bar_name.title()}."