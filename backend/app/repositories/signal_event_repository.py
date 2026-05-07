from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.signal_event import SignalEvent


class SignalEventRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_by_scan(self, scan_id: str) -> list[SignalEvent]:
        stmt = select(SignalEvent).where(SignalEvent.scan_id == scan_id).order_by(SignalEvent.created_at.asc())
        return list(self.db.scalars(stmt).all())

    def create_many(self, items: list[SignalEvent]) -> list[SignalEvent]:
        if not items:
            return []

        existing_keys = {
            self._dedupe_key(item)
            for item in self.list_by_scan(items[0].scan_id or "")
        }
        created: list[SignalEvent] = []
        for item in items:
            dedupe_key = self._dedupe_key(item)
            if dedupe_key in existing_keys:
                continue
            self.db.add(item)
            created.append(item)
            existing_keys.add(dedupe_key)

        self.db.flush()
        return created

    @staticmethod
    def _dedupe_key(item: SignalEvent) -> tuple[str | None, str | None, str | None, str]:
        payload = item.raw_payload or {}
        signature = payload.get("signature")
        return (item.wallet_id, item.asset_id, signature, item.event_type)
