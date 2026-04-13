from __future__ import annotations

import logging
from typing import Any

from database.sessionmaker import Session
from models.users_model import GameEvent

logger = logging.getLogger(__name__)


def create_game_event(
    user_id: int,
    event_type: str,
    summary: str,
    event_data: dict[str, Any] | None = None,
    *,
    keep_recent: int | None = None,
) -> int:
    """Persist a user-facing gameplay memory event."""
    payload = event_data or {}
    keep_recent = max(keep_recent, 1) if keep_recent is not None else None

    with Session() as session:
        try:
            event = GameEvent(
                user_id=user_id,
                event_type=event_type,
                summary=summary,
                event_data=payload,
            )
            session.add(event)
            session.flush()

            if keep_recent is not None:
                _trim_event_type(session, user_id, event_type, keep_recent)

            session.commit()
            return event.id
        except Exception:
            session.rollback()
            logger.exception("Failed to persist game event for user %s", user_id)
            return 0


def get_recent_game_events(user_id: int, limit: int = 10) -> list[dict[str, Any]]:
    """Return the user's most recent gameplay events in chronological order."""
    if limit <= 0:
        return []

    with Session() as session:
        try:
            events = (
                session.query(GameEvent)
                .filter(GameEvent.user_id == user_id)
                .order_by(GameEvent.created_at.desc(), GameEvent.id.desc())
                .limit(limit)
                .all()
            )
        except Exception:
            logger.exception("Failed to fetch recent game events for user %s", user_id)
            return []

    serialized = [
        {
            "id": event.id,
            "event_type": event.event_type,
            "summary": event.summary,
            "event_data": event.event_data or {},
            "created_at": event.created_at.isoformat() if event.created_at else None,
        }
        for event in reversed(events)
    ]
    return serialized


def remove_referenced_game_event(event_id: int) -> bool:
    """Delete a game event once downstream memory logic decides it was consumed."""
    with Session() as session:
        try:
            deleted = (
                session.query(GameEvent)
                .filter(GameEvent.id == event_id)
                .delete(synchronize_session=False)
            )
            session.commit()
            return bool(deleted)
        except Exception:
            session.rollback()
            logger.exception("Failed to delete referenced game event %s", event_id)
            return False


def _trim_event_type(session, user_id: int, event_type: str, keep_recent: int) -> None:
    stale_ids = [
        event_id
        for (event_id,) in (
            session.query(GameEvent.id)
            .filter(
                GameEvent.user_id == user_id,
                GameEvent.event_type == event_type,
            )
            .order_by(GameEvent.created_at.desc(), GameEvent.id.desc())
            .offset(keep_recent)
            .all()
        )
    ]

    if stale_ids:
        (
            session.query(GameEvent)
            .filter(GameEvent.id.in_(stale_ids))
            .delete(synchronize_session=False)
        )
