from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Tuple, Optional

from sqlalchemy import select

from database.sessionmaker import Session

from models.users_model import Loan

from domain.loans.rules import get_loan_period

def issue_loan(user_id: int, loan_pack_id: str) -> Tuple[bool, Optional[int], Optional[Loan]]:
    """Issue a loan to a user if they don't already have an active one.

    Returns:
        (ok, active_pack_id, loan_row)

        - ok=True: loan was created, loan_row is returned
        - ok=False: user already has an active loan, active_pack_id contains the existing pack id

    Notes:
        - This function only creates the `loans` record.
        - It does NOT credit gold
    """
    duration_days = get_loan_period(loan_pack_id)
    with Session() as session:
        #Check if user already has an active loan
        existing_active: Loan | None = session.execute(
            select(Loan)
            .where(Loan.user_id == user_id)
            .where(Loan.status == 'active')
            .limit(1)
        ).scalar_one_or_none()

        if existing_active is not None:
            # already has an active loan
            return False, int(existing_active.loan_pack_id), None

        #Create new loan record
        now = datetime.now(timezone.utc)
        due_date = now + timedelta(days=duration_days)

        new_loan = Loan(
            user_id=user_id,
            loan_pack_id=int(loan_pack_id),
            status='active',
            issued_at=now,
            due_date=due_date,
        )

        session.add(new_loan)
        session.commit()
        session.refresh(new_loan)

        return True, None, new_loan
