"""Idempotent seed helpers for DB-defined content."""

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import sessionmaker

from database.seed_data import ITEMS, UPGRADE_DEFINITIONS
from models.inventory_model import Items
from models.users_model import UpgradeDefinitions


def _upsert_rows(session, model, rows, conflict_columns):
    if not rows:
        return 0

    table = model.__table__
    stmt = insert(table).values(rows)
    update_columns = {
        column.name: getattr(stmt.excluded, column.name)
        for column in table.columns
        if column.name not in conflict_columns
    }

    session.execute(
        stmt.on_conflict_do_update(
            index_elements=list(conflict_columns),
            set_=update_columns,
        )
    )
    return len(rows)


def seed_core_data(engine) -> dict[str, int]:
    """Seed item and upgrade definition rows from source-controlled data."""
    SessionLocal = sessionmaker(bind=engine)

    with SessionLocal() as session:
        counts = {
            "items": _upsert_rows(session, Items, ITEMS, ("item_id",)),
            "upgrade_definitions": _upsert_rows(
                session,
                UpgradeDefinitions,
                UPGRADE_DEFINITIONS,
                ("upgrade_name", "level"),
            ),
        }
        session.commit()

    return counts
