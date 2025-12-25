from services.economy_services import add_gold, remove_gold
from utils.custom_errors import NotEnoughGoldError
import pytest

def test_transfer_gold_success(session, user_a, user_b):
    # arrange
    user_a.wallet.gold = 100
    session.commit()

    # act
    add_gold(user_b.user_id, 50)
    remove_gold(user_a.user_id, 50)

    # assert
    session.refresh(user_a.wallet)
    session.refresh(user_b.wallet)

    assert user_a.wallet.gold == 50
    assert user_b.wallet.gold == 50

def test_transfer_gold_insufficient_funds(session, user_a, user_b):
    # arrange
    user_a.wallet.gold = 10
    user_b.wallet.gold = 0
    session.commit()

    # act
    with pytest.raises(NotEnoughGoldError):
        remove_gold(user_a.user_id, 50)

    # assert
    session.refresh(user_a.wallet)
    session.refresh(user_b.wallet)

    assert user_a.wallet.gold == 10
    assert user_b.wallet.gold == 0