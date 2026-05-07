import sys
import types

sessionmaker_stub = types.ModuleType("database.sessionmaker")
sessionmaker_stub.Session = lambda: None
sys.modules["database.sessionmaker"] = sessionmaker_stub

from services import inventory_services, marketplace_services


class FakeSession:
    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False


def test_account_bound_mythic_shards_cannot_be_marketplace_listed():
    assert marketplace_services.create_listing(123, 3006, 1, 500) == -2
    assert marketplace_services.create_listing(123, 3007, 1, 500) == -2


def test_account_bound_mythic_shards_cannot_be_transferred(monkeypatch):
    monkeypatch.setattr(inventory_services, "Session", lambda: FakeSession())
    monkeypatch.setattr(inventory_services, "is_user", lambda *_args: True)

    assert inventory_services.transfer_item(1, 2, 3006, 1) == "account_bound"
