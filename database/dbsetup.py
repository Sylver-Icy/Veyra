import os
import sys


if __package__ is None:
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database.sessionmaker import ensure_schema


if __name__ == "__main__":
    ensure_schema()
    print("All ORM tables and core seed rows created or already present.")
