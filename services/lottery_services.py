import random

from sqlalchemy.orm.attributes import flag_modified

from database.sessionmaker import Session
from models.users_model import LotteryEntries

from services.economy_services import check_wallet, remove_gold

from utils.custom_errors import UserNotFoundError

tickets_created = set()

def create_ticket(user_id: int, ticket_price: int):
    """
    create a lottery draw ticket

    """
    # return 0 if user doesn't have money for ticket
    if ticket_price > check_wallet(user_id):
        return 0
    try:
        remove_gold(user_id, ticket_price)
    except UserNotFoundError:
        return 1  # return 1 if unregistered user tries to buy tickets

    ticket_id = random.randint(1000000, 9999999)
    while ticket_id in tickets_created:
        ticket_id = random.randint(1000000, 9999999)
    tickets_created.add(ticket_id)

    with Session() as session:
        entry = session.get(LotteryEntries, user_id)
        if entry:
            entry.tickets = entry.tickets + [ticket_id]
        else:
            entry = LotteryEntries(
                user_id=user_id,
                tickets=[ticket_id],
                ticket_price=ticket_price
            )
            session.add(entry)

        session.commit()
        return ticket_id



def get_user_tickets(user_id: int):
    with Session() as session:
        entry = session.query(LotteryEntries).filter_by(user_id=user_id).first()
        return entry.tickets if entry else []


def pick_lottery_winner():
    with Session() as session:
        all_entries = session.query(LotteryEntries).all()
        if not all_entries:
            return None

        all_tickets = [(e.user_id, t) for e in all_entries for t in e.tickets]
        if not all_tickets:
            return None

        winner_user_id, winning_ticket = random.choice(all_tickets)

        return winner_user_id, winning_ticket


def reset_lottery():
    with Session() as session:
        session.query(LotteryEntries).delete()
        session.commit()
    tickets_created.clear()


def calculate_prize_pool():
    """Calculate the total gold in the prize pool based on all tickets sold."""
    with Session() as session:
        entries = session.query(LotteryEntries).all()
        if not entries:
            return 0

        total = 0
        for entry in entries:
            print(entry.tickets)
            total += len(entry.tickets) * entry.ticket_price
        print (total)
        return total