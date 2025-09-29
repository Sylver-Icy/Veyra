from models.inventory_model import Items
from database.sessionmaker import Session
from rapidfuzz import process

def load_item_map():
    """Loads Items table into a dictionary of item names to IDs"""
    with Session() as session:
        return {
            item.item_name.lower(): item.item_id
            for item in session.query(Items).all()
        }

item_name_to_id = load_item_map()

def suggest_similar_item(user_input: str, limit: int = 3, threshold: int = 65):
    """
    Uses rapidfuzz to suggest up to `limit` similar items if user input doesn't match exactly.
    Only returns suggestions with a score above `threshold`.
    """
    choices = list(item_name_to_id.keys())
    results = process.extract(user_input, choices, limit=limit)
    return [match for match, score, _ in results if score >= threshold]

def get_item_id_safe(user_input: str):
    """
    Attempts to fetch the item ID using a case-insensitive name match.
    If not found, returns None and a list of suggested similar items.
    """
    item_id = item_name_to_id.get(user_input.lower())
    if item_id is not None:
        return item_id, [] #if perfect match is found return the item id with empty list for suggestions
    suggestions = suggest_similar_item(user_input)
    return None, suggestions
