from app.workers.queue import InMemoryQueueClient


def test_in_memory_queue_dequeues_jobs_fifo() -> None:
    queue = InMemoryQueueClient()
    queue.enqueue("scan", {"scan_id": "scan-1"})
    queue.enqueue("scan", {"scan_id": "scan-2"})

    assert queue.dequeue("scan") == {"scan_id": "scan-1"}
    assert queue.dequeue("scan") == {"scan_id": "scan-2"}
    assert queue.dequeue("scan") is None
