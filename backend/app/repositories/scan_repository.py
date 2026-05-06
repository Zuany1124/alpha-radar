from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.scan import Scan
from app.models.mixins import now_utc
from app.schemas.scan import ScanCreate


class ScanRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self, limit: int = 50, offset: int = 0) -> list[Scan]:
        return list(self.db.scalars(select(Scan).offset(offset).limit(limit)).all())

    def get(self, scan_id: str) -> Scan | None:
        return self.db.get(Scan, scan_id)

    def create(self, payload: ScanCreate) -> Scan:
        scan = Scan(trigger=payload.trigger, scope=payload.scope, status="queued")
        self.db.add(scan)
        self.db.commit()
        self.db.refresh(scan)
        return scan

    def mark_running(self, scan_id: str) -> Scan | None:
        scan = self.get(scan_id)
        if scan is None:
            return None
        scan.status = "running"
        scan.started_at = now_utc()
        scan.error_message = None
        self.db.commit()
        self.db.refresh(scan)
        return scan

    def mark_succeeded(
        self,
        scan_id: str,
        created_signal_event_count: int,
        created_lead_count: int,
    ) -> Scan | None:
        scan = self.get(scan_id)
        if scan is None:
            return None
        scan.status = "succeeded"
        scan.finished_at = now_utc()
        scan.error_message = None
        scan.created_signal_event_count = created_signal_event_count
        scan.created_lead_count = created_lead_count
        self.db.commit()
        self.db.refresh(scan)
        return scan

    def mark_failed(self, scan_id: str, error_message: str) -> Scan | None:
        scan = self.get(scan_id)
        if scan is None:
            return None
        scan.status = "failed"
        scan.finished_at = now_utc()
        scan.error_message = error_message
        self.db.commit()
        self.db.refresh(scan)
        return scan
