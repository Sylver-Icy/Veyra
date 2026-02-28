from sqlalchemy import select, func

from database.sessionmaker import Session
from models.inventory_model import Inventory
from models.marketplace_model import Marketplace, ShopDaily

from services.economy_services import remove_gold

from utils.itemname_to_id import get_item_id_safe
from utils.custom_errors import NotEnoughGoldError
from utils.emotes import GOLD_EMOJI

def lookup_item_sources(user_id: int, item_name: str):
    """
    Look up possible sources for a given item and charge a small gold fee.

    This function:
    - Resolves the provided item name using fuzzy matching.
    - Charges the user a spy fee (if the item exists).
    - Checks the Daily Shop, Marketplace, and player inventories.
    - Returns a structured dictionary describing all discovered leads.

    Args:
        user_id (int): The Discord user ID.
        item_name (str): The name of the item to search for.

    Returns:
        dict: {
            "shop": bool,
            "marketplace": list[int],
            "players": list[int],
            "message": str
        }
    """

    SPY_COST = 25

    # Resolve item name using fuzzy-safe util
    item_id, suggestions = get_item_id_safe(item_name)

    if item_id is None:
        return {
            "shop": False,
            "marketplace": [],
            "players": [],
            "message": (
                "❌ Item not recognized.\n"
                + ("Did you mean: " + ", ".join(suggestions) if suggestions else "")
            )
        }

    try:
        with Session() as session:
            remove_gold(user_id, SPY_COST, session)
            session.commit()
    except NotEnoughGoldError:
        return {
            "shop": False,
            "marketplace": [],
            "players": [],
            "message": f"🕵️ I ain't running errands for free. Come back with {SPY_COST} {GOLD_EMOJI}."
        }

    result = {
        "shop": False,
        "marketplace": [],
        "players": [],
        "message": ""
    }

    with Session() as session:

        # --- Shop ---
        latest_date = session.execute(
            select(func.max(ShopDaily.date))
        ).scalar()

        shop_item = session.execute(
            select(ShopDaily)
            .where(
                ShopDaily.item_id == item_id,
                ShopDaily.date == latest_date,
                ShopDaily.shop_type == "sell"
            )
        ).scalars().first()

        if shop_item:
            result["shop"] = True

        # --- Marketplace (limit 3) ---
        mp_items = session.execute(
            select(Marketplace)
            .where(Marketplace.item_id == item_id)
            .limit(3)
        ).scalars().all()

        result["marketplace"] = [m.listing_id for m in mp_items]

        # --- Player inventories (limit 3) ---
        owners = session.execute(
            select(Inventory.user_id)
            .distinct()
            .where(
                Inventory.item_id == item_id,
                Inventory.item_quantity > 0
            )
            .limit(3)
        ).scalars().all()

        result["players"] = owners

    # -----------------------------
    # Build response message
    # -----------------------------
    lines = []

    if result["shop"]:
        lines.append("🏪 Available in Daily Shop. Check out `/shop`")

    if result["marketplace"]:
        ids = ", ".join(str(i) for i in result["marketplace"])
        lines.append(f"🛒 Spotted on the marketplace (listing IDs: {ids}).")

    if result["players"]:
        mentions = ", ".join(f"<@{u}>" for u in result["players"])
        lines.append(f"👤 Rumor says these players own at least one: {mentions}")

    if not lines:
        lines.append(
            "❌ No leads found.\n"
            "Try waiting for a shop reroll, opening boxes, or running explorer jobs and praying to RNGesus."
        )

    result["message"] = "\n".join(lines)

    return result