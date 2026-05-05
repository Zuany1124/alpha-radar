import json

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.repositories.scan_repository import ScanRepository
from app.workers.queue import InMemoryQueueClient
from app.workers.runner import ScanWorkerRunner


def test_manual_scan_creates_queued_record_and_enqueues_job(
    client: TestClient, queue_client: InMemoryQueueClient
) -> None:
    response = client.post("/api/v1/scans", json={"trigger": "manual", "scope": {"wallet_ids": ["wallet-1"]}})

    assert response.status_code == 201
    scan = response.json()
    assert scan["status"] == "queued"
    assert scan["trigger"] == "manual"
    assert queue_client.enqueued_jobs == [{"job_name": "scan", "payload": {"scan_id": scan["id"]}}]

    detail_response = client.get(f"/api/v1/scans/{scan['id']}")
    assert detail_response.status_code == 200
    assert detail_response.json()["id"] == scan["id"]


def test_scan_worker_consumes_job_and_marks_scan_succeeded(
    client: TestClient,
    db_session: Session,
    queue_client: InMemoryQueueClient,
) -> None:
    response = client.post("/api/v1/scans", json={"trigger": "manual", "scope": {"wallet_ids": ["wallet-1"]}})
    scan_id = response.json()["id"]

    runner = ScanWorkerRunner(ScanRepository(db_session), queue_client)

    assert runner.run_once() is True

    detail_response = client.get(f"/api/v1/scans/{scan_id}")
    scan = detail_response.json()
    assert scan["status"] == "succeeded"
    assert scan["started_at"] is not None
    assert scan["finished_at"] is not None
    assert scan["error_message"] is None
    assert scan["created_signal_event_count"] == 0
    assert scan["created_lead_count"] == 0


def test_scan_worker_marks_scan_failed_when_job_raises(
    client: TestClient,
    db_session: Session,
    queue_client: InMemoryQueueClient,
    monkeypatch,
) -> None:
    response = client.post("/api/v1/scans", json={"trigger": "manual", "scope": {"wallet_ids": ["wallet-1"]}})
    scan_id = response.json()["id"]

    def fail_scan_job(scan_id: str) -> dict:
        raise RuntimeError(f"scan failed: {scan_id}")

    monkeypatch.setattr("app.workers.runner.run_scan_job", fail_scan_job)
    runner = ScanWorkerRunner(ScanRepository(db_session), queue_client)

    assert runner.run_once() is True

    detail_response = client.get(f"/api/v1/scans/{scan_id}")
    scan = detail_response.json()
    assert scan["status"] == "failed"
    assert scan["started_at"] is not None
    assert scan["finished_at"] is not None
    assert "scan failed" in scan["error_message"]


def test_scan_worker_skips_invalid_json_payload(db_session: Session) -> None:
    class InvalidJsonQueue:
        def enqueue(self, job_name: str, payload: dict) -> None:
            raise NotImplementedError

        def dequeue(self, job_name: str, timeout_seconds: int = 5) -> dict | None:
            raise json.JSONDecodeError("bad json", "{", 0)

        def ping(self) -> bool:
            return True

    runner = ScanWorkerRunner(ScanRepository(db_session), InvalidJsonQueue())

    assert runner.run_once() is True
