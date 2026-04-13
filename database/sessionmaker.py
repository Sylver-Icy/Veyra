import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


load_dotenv("veyra.env")
DB_URL = os.getenv("DB_URL")
TEST_DB_URL = os.getenv("TEST_DB_URL")

engine = create_engine(DB_URL)
# For testing purposes, you can switch to TEST_DB_URL
# engine = create_engine(TEST_DB_URL)

Session = sessionmaker(bind=engine)

_schema_initialized = False


def ensure_schema() -> None:
    """Create any ORM-managed tables that do not already exist."""
    global _schema_initialized
    if _schema_initialized:
        return

    import models  # noqa: F401 - ensures all ORM model modules are registered
    from models.users_model import Base

    Base.metadata.create_all(bind=engine)
    _schema_initialized = True


ensure_schema()


