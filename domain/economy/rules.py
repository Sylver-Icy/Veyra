from domain.shared.types import Gold
from domain.shared.errors import InvalidAmountError, InsufficientFundsError

TRANSFER_FEE_RATE = 0.05

def validate_transfer_amount(amount: int) -> Gold:
    if amount <= 0:
        raise InvalidAmountError("Amount must be positive")
    return Gold(amount)

def calculate_transfer_fee(amount: Gold) -> tuple[Gold, Gold]:
    fee = Gold(int(amount * TRANSFER_FEE_RATE))
    return Gold(amount - fee), fee

def ensure_can_afford(balance: Gold, amount: Gold) -> None:
    if balance < amount:
        raise InsufficientFundsError(amount, balance)