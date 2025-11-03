import re
from models.inventory_model import Items
from database.sessionmaker import Session
from rapidfuzz import process


def clean_name(name: str) -> str:
    """Removes all non-alphabetic characters and converts to lowercase."""
    return re.sub(r'[^a-z ]', '', name.lower())


def load_item_map():
    """Loads Items table into a dictionary of simplified (letters only) item names to IDs."""
    with Session() as session:
        return {
            clean_name(item.item_name): item.item_id
            for item in session.query(Items).all()
        }


item_name_to_id = load_item_map()


def suggest_similar_item(user_input: str, limit: int = 3, threshold: int = 75):
    """
    Uses rapidfuzz to suggest up to `limit` similar items if user input doesn't match exactly.
    Only returns suggestions with a score above `threshold`.
    """
    user_input = clean_name(user_input)
    choices = list(item_name_to_id.keys())
    results = process.extract(user_input, choices, limit=limit)
    return [match.capitalize() for match, score, _ in results if score >= threshold]


def get_item_id_safe(user_input: str):
    """
    Attempts to fetch the item ID using a simplified, case-insensitive match.
    If not found, returns None and a list of suggested similar items.
    """
    cleaned_input = clean_name(user_input)
    item_id = item_name_to_id.get(cleaned_input)
    if item_id is not None:
        return item_id, []  # perfect match
    suggestions = suggest_similar_item(cleaned_input)
    return None, suggestions
