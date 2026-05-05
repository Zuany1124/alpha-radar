from fastapi import HTTPException, status

from app.models.scan import Scan
from app.repositories.scan_repository import ScanRepository
from app.schemas.scan import ScanCreate
from app.workers.queue import QueueClient


class ScanService:
    def __init__(self, scans: ScanRepository, queue: QueueClient) -> None:
        self.scans = scans
        self.queue = queue

    def list_scans(self, limit: int, offset: int) -> list[Scan]:
        return self.scans.list(limit=limit, offset=offset)

    def get_scan(self, scan_id: str) -> Scan:
        scan = self.scans.get(scan_id)
        if scan is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found")
        return scan

    def create_scan(self, payload: ScanCreate) -> Scan:
        scan = self.scans.create(payload)
        self.queue.enqueue("scan", {"scan_id": scan.id})
        return scan
