from services.inventory_services import give_item, take_item

from domain.crafting.rules import validate_smelt_amount, get_required_ore, required_ore_amount
from domain.shared.errors import InvalidAmountError, InvalidRecipeError

from utils.itemname_to_id import get_item_id_safe
from utils.custom_errors import NotEnoughItemError


def smelt(user_id: int, bar_name: str, amount: int, coal_cost: int):
    """
    Smelts a specified amount of bars for a user by consuming ores and coal.

    Parameters:
        user_id (int): The ID of the user performing the smelting.
        bar_name (str): The name of the bar to smelt.
        amount (int): The number of bars to smelt.

    Returns:
        str: A message indicating success or the reason for failure.

    Raises:
        NotEnoughItemError: If the user does not have enough ores or coal.
    """
    # Normalize bar name to lowercase
    bar_name = bar_name.lower()

    # Validate smelting amount
    try:
        amount = validate_smelt_amount(amount)
    except InvalidAmountError:
        return "Smelt amount must be positive."

    # Get required ore for the specified bar
    try:
        ore_name = get_required_ore(bar_name)
    except InvalidRecipeError:
        return f"'{bar_name}' is not a valid bar to smelt."

    # Retrieve ore and bar item IDs
    ore_id, _ = get_item_id_safe(ore_name)
    bar_id, _ = get_item_id_safe(bar_name)
    coal_id, _ = get_item_id_safe("coal")

    # Attempt to consume required ores
    try:
        ore_needed = required_ore_amount(amount)
        take_item(user_id, ore_id, ore_needed)

    except NotEnoughItemError:
        return "Not enough ores to smelt."

    # Attempt to consume required coal, refund ores if insufficient
    try:
        take_item(user_id, coal_id, amount * coal_cost)

    except NotEnoughItemError:
        give_item(user_id, ore_id, ore_needed)
        return "Not enough coal to smelt."

    # Give smelted bars to user
    give_item(user_id, bar_id, amount)
    return f"🔥 Successfully smelted {amount}x {bar_name.title()}."