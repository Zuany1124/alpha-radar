import json
import logging

from app.core.config import get_settings
from app.db.session import SessionLocal
from app.repositories.scan_repository import ScanRepository
from app.workers.jobs.scan_job import run_scan_job
from app.workers.queue import QueueClient, RedisQueueClient

logger = logging.getLogger(__name__)


class ScanWorkerRunner:
    """Scan worker runner，消费队列并回写 Scan 状态"""

    def __init__(self, scans: ScanRepository, queue: QueueClient) -> None:
        self.scans = scans
        self.queue = queue

    def run_once(self, timeout_seconds: int = 5) -> bool:
        """消费并执行一个 scan job

        Args:
            timeout_seconds: 队列阻塞等待秒数

        Returns:
            是否消费到 job
        """
        try:
            payload = self.queue.dequeue("scan", timeout_seconds=timeout_seconds)
        except json.JSONDecodeError:
            logger.exception("Invalid scan job JSON payload")
            return True

        if payload is None:
            return False

        scan_id = payload.get("scan_id")
        if not scan_id:
            logger.error("Scan job missing scan_id: %s", payload)
            return True

        self.scans.mark_running(scan_id)
        try:
            result = run_scan_job(scan_id)
        except Exception as exc:
            logger.exception("Scan job failed: %s", scan_id)
            self.scans.mark_failed(scan_id, str(exc))
            return True

        self.scans.mark_succeeded(
            scan_id,
            created_signal_event_count=result.get("created_signal_event_count", 0),
            created_lead_count=result.get("created_lead_count", 0),
        )
        return True

    def run_forever(self) -> None:
        """持续消费 scan job"""
        while True:
            self.run_once()


def build_runner() -> ScanWorkerRunner:
    """创建独立 worker runner"""
    settings = get_settings()
    db = SessionLocal()
    return ScanWorkerRunner(ScanRepository(db), RedisQueueClient(settings.redis_url))


def main() -> None:
    """Worker CLI 入口"""
    build_runner().run_forever()


if __name__ == "__main__":
    main()
