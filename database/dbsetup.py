from database.sessionmaker import ensure_schema


if __name__ == "__main__":
    ensure_schema()
    print("All ORM tables created or already present.")
