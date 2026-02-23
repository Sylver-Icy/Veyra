import asyncio
import importlib
import os
import sqlite3
import sys
from types import SimpleNamespace


def load_jobs_cog():
    db_url = os.getenv("DB_URL", "")
    if db_url.startswith("sqlite:///"):
        db_path = db_url.removeprefix("sqlite:///")
        with sqlite3.connect(db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS items (
                    item_id INTEGER PRIMARY KEY,
                    item_name TEXT UNIQUE NOT NULL,
                    item_description TEXT NOT NULL,
                    item_rarity TEXT NOT NULL,
                    item_icon TEXT,
                    item_durability INTEGER,
                    item_price INTEGER NOT NULL,
                    item_usable BOOLEAN NOT NULL DEFAULT 0
                )
                """
            )

    if "cogs.jobs" in sys.modules:
        return importlib.reload(sys.modules["cogs.jobs"])
    return importlib.import_module("cogs.jobs")


class DummyCtx:
    def __init__(self):
        self.author = SimpleNamespace(id=42)
        self.messages = []

    async def respond(self, content):
        self.messages.append(content)


def test_work_requires_target_for_thief(monkeypatch):
    jobs_cog = load_jobs_cog()

    class Worker:
        def __init__(self, user_id):
            self.user_id = user_id
            self.thief_called = False

        def knight(self):
            return "knight"

        def digger(self):
            return "digger"

        def miner(self):
            return "miner"

        def explorer(self):
            return "explorer"

        def thief(self, target):
            self.thief_called = True
            return "thief"

    monkeypatch.setattr(jobs_cog, "JobsClass", Worker)
    ctx = DummyCtx()
    cog = jobs_cog.Jobs(bot=None)

    asyncio.run(jobs_cog.Jobs.work.callback(cog, ctx, "thief", None))

    assert ctx.messages == ["You need to specify someone to steal from! You can't rob air can you?"]


def test_work_runs_selected_job(monkeypatch):
    jobs_cog = load_jobs_cog()

    class Worker:
        def __init__(self, user_id):
            self.user_id = user_id

        def knight(self):
            return "knight-result"

        def digger(self):
            return "digger-result"

        def miner(self):
            return "miner-result"

        def explorer(self):
            return "explorer-result"

        def thief(self, target):
            return "thief-result"

    monkeypatch.setattr(jobs_cog, "JobsClass", Worker)
    ctx = DummyCtx()
    cog = jobs_cog.Jobs(bot=None)

    asyncio.run(jobs_cog.Jobs.work.callback(cog, ctx, "digger", None))

    assert ctx.messages == ["digger-result"]
