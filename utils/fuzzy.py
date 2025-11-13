from rapidfuzz import process, fuzz



commands = ("ping", "checkwallet", "checkexp", "checkinventory", "unlock", "upgrade", "bet", "flipcoin", "play", "use", "info", "work", "open", "commandhelp", "helloveyra", "buy", "sell" )

def get_closest_command(cmd: str):
    """
    Returns the closest valid command name based on fuzzy matching.
    If no command is at least 60% similar, returns None.
    """
    match, score, _ = process.extractOne(
        cmd,
        commands,
        scorer=fuzz.ratio
    )
    if score >= 60:
        return match
    return None