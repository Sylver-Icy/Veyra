from datetime import datetime, timezone

def today():
    return datetime.now(timezone.utc).date()