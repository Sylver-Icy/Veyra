class VeyraError(Exception):
    """Base class for all the bot errors"""
    def __init__(self, message="An error occured in Veyra"):
        self.message = message
        super().__init__(self.message)

class NotEnoughGoldError(VeyraError):
    """Raise error when user tries to spend more than they have in wallet"""
    def __init__(self, gold_required, gold_available):
        message = f"You are too broke!!!!!!! don't have enough gold. Required{gold_required}, Available{gold_available}"
        super().__init__(message)

class UserNotFoundError(VeyraError):
    """Raise error when user is not in database"""

    def __init__(self, user_id):
        message = f"<@{user_id}> is not my friend, can't interact! Stranger Danger"
        super().__init__(message)

class NegativeGoldError(VeyraError):
    """Raise error if someone tries adding negative gold"""
    def __init__(self):
        message = "Mind explaining me why you want to transfer negative gold? ._."
        super().__init__(message)

class WrongItemError(VeyraError):
    """Raise error if there is no such item in database"""
    def __init__(self):
        message = "There is no such item"
        super().__init__(message)
