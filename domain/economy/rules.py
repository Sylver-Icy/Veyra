from domain.shared.types import Gold
from domain.shared.errors import InvalidAmountError, InsufficientFundsError

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Percentage fee applied to gold transfers (5%)
TRANSFER_FEE_RATE = 0.05


# ---------------------------------------------------------------------------
# Validation & calculation rules
# ---------------------------------------------------------------------------

def validate_transfer_amount(amount: int) -> Gold:
    """
    Validate that a transfer amount is positive and convert it to Gold.

    Args:
        amount (int): Raw transfer amount

    Returns:
        Gold: Validated gold amount

    Raises:
        InvalidAmountError: If the amount is zero or negative
    """
    if amount <= 0:
        raise InvalidAmountError("Amount must be positive")

    return Gold(amount)


def calculate_transfer_fee(amount: Gold) -> tuple[Gold, Gold]:
    """
    Calculate the transfer fee and net amount after deduction.

    Args:
        amount (Gold): Amount being transferred

    Returns:
        tuple[Gold, Gold]: (net_amount, fee)
    """
    fee = Gold(int(amount * TRANSFER_FEE_RATE))
    net_amount = Gold(amount - fee)

    return net_amount, fee


def ensure_can_afford(balance: Gold, amount: Gold) -> None:
    """
    Ensure the user has enough gold to afford a transfer.

    Args:
        balance (Gold): User's current balance
        amount (Gold): Amount required

    Raises:
        InsufficientFundsError: If balance is insufficient
    """
    if balance < amount:
        raise InsufficientFundsError(amount, balance)