from discord.ext import commands
class VeyraError(commands.CommandError):
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

class InvalidItemAmountError(VeyraError):
    """Same as gold but for items"""
    def __init__(self):
        message = "That's not a valid amount"
        super().__init__(message)

class WrongItemError(VeyraError):
    """Raise error if there is no such item in database"""
    def __init__(self):
        message = "There is no such item"
        super().__init__(message)

class NotEnoughItemError(VeyraError):
    """Raise error when user has insuffiecient items for transaction"""
    def __init__(self):
        message = "You don't own enough items"
        super().__init__(message)

class WrongInputError(VeyraError):
    """Raise error if wrong input for wordle solver"""
    def __init__(self):
        message = "Wrong input try again!"
        super().__init__(message)

class NoValidWordsError(VeyraError):
    """Raise error if wordle has  no possible words left"""

    def __init__(self):
        message = "I tried all 5 letter words nothing left prolly wrong inputs from your side or maybe you looking for some alien language word"
        super().__init__(message)

class PolicyError(VeyraError):
    """Base error for server/channel policy restrictions"""
    def __init__(self, message="This action is restricted by server policies"):
        super().__init__(message)


class WrongChannelError(PolicyError):
    """Raised when a command is used in a disallowed channel"""
    def __init__(self, message="This command is not allowed in this channel"):
        super().__init__(message)


class ServerRestrictedError(PolicyError):
    """Raised when a command/feature is disabled in a specific server"""
    def __init__(self, message="This command is restricted in this server"):
        super().__init__(message)