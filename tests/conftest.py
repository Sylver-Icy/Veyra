import pytest
from database.sessionmaker import Session
from models.users_model import User, Wallet

def get_or_create_user_with_wallet(session, user_id: int, user_name: str):
    user = session.query(User).filter_by(user_id=user_id).first()
    if user:
        return user
    user = User(
        user_id=user_id,
        user_name=user_name,
        joined="2024-01-01 00:00:00"
    )
    wallet = Wallet(user_id=user_id, gold=0)
    session.add_all([user, wallet])
    session.commit()
    return user

@pytest.fixture
def session():
    session = Session()
    yield session
    session.rollback()
    session.close()

@pytest.fixture
def user_a(session):
    return get_or_create_user_with_wallet(session, 1, "UserA")

@pytest.fixture
def user_b(session):
    return get_or_create_user_with_wallet(session, 2, "UserB")