class DomainError(Exception):
    pass

class InvalidAmountError(DomainError):
    pass

class InsufficientFundsError(DomainError):
    def __init__(self, required, available):
        super().__init__(f"Required {required}, but only {available} available")

class InvalidRecipeError(DomainError):
    def __init__(self, recipe_name):
        super().__init__(f"Invalid recipe: {recipe_name}")