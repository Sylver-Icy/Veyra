import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker


load_dotenv("veyra.env")
DB_URL = os.getenv("DB_URL")
TEST_DB_URL = os.getenv("TEST_DB_URL")

engine = create_engine(DB_URL)
# For testing purposes, you can switch to TEST_DB_URL
# engine = create_engine(TEST_DB_URL)

Session = sessionmaker(bind=engine)

_schema_initialized = False


def ensure_item_type_column() -> None:
    """Keep pre-reset/local DBs compatible with the item type split."""
    inspector = inspect(engine)
    if not inspector.has_table("items"):
        return

    column_names = {column["name"] for column in inspector.get_columns("items")}
    with engine.begin() as conn:
        if "item_type" not in column_names:
            conn.execute(text("ALTER TABLE items ADD COLUMN item_type VARCHAR"))
        conn.execute(text("UPDATE items SET item_type = 'item' WHERE item_type IS NULL"))
        conn.execute(text("UPDATE items SET item_type = 'lootbox', item_rarity = 'Common' WHERE item_rarity = 'lootbox'"))
        conn.execute(text("UPDATE items SET item_type = 'mineral', item_rarity = 'Common' WHERE item_rarity = 'minerals'"))
        conn.execute(text("UPDATE items SET item_type = 'potion', item_rarity = 'Common' WHERE item_rarity = 'Potion'"))
        conn.execute(text("ALTER TABLE items ALTER COLUMN item_type SET DEFAULT 'item'"))
        conn.execute(text("ALTER TABLE items ALTER COLUMN item_type SET NOT NULL"))


def ensure_schema() -> None:
    """Create any ORM-managed tables that do not already exist."""
    global _schema_initialized
    if _schema_initialized:
        return

    import models  # noqa: F401 - ensures all ORM model modules are registered
    from models.users_model import Base

    Base.metadata.create_all(bind=engine)
    ensure_item_type_column()

    from database.seed import seed_core_data

    seed_core_data(engine)
    _schema_initialized = True


ensure_schema()
