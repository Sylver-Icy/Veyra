from dataclasses import dataclass
from domain.shared.types import Gold

@dataclass(frozen=True)
class TransferResult:
    sender_balance: Gold
    receiver_balance: Gold
    amount_transferred: Gold
    fee_charged: Gold