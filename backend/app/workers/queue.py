import json
from typing import Protocol

from redis import Redis


class QueueClient(Protocol):
    def enqueue(self, job_name: str, payload: dict) -> None:
        ...

    def dequeue(self, job_name: str, timeout_seconds: int = 5) -> dict | None:
        ...

    def ping(self) -> bool:
        ...


class RedisQueueClient:
    def __init__(self, redis_url: str) -> None:
        self.redis_url = redis_url
        self._redis = Redis.from_url(redis_url, decode_responses=True)

    def enqueue(self, job_name: str, payload: dict) -> None:
        self._redis.rpush(f"alpharadar:jobs:{job_name}", json.dumps(payload))

    def dequeue(self, job_name: str, timeout_seconds: int = 5) -> dict | None:
        result = self._redis.blpop(f"alpharadar:jobs:{job_name}", timeout=timeout_seconds)
        if result is None:
            return None
        _, raw_payload = result
        return json.loads(raw_payload)

    def ping(self) -> bool:
        return bool(self._redis.ping())


class InMemoryQueueClient:
    def __init__(self) -> None:
        self.enqueued_jobs: list[dict] = []

    def enqueue(self, job_name: str, payload: dict) -> None:
        self.enqueued_jobs.append({"job_name": job_name, "payload": payload})

    def dequeue(self, job_name: str, timeout_seconds: int = 5) -> dict | None:
        for index, job in enumerate(self.enqueued_jobs):
            if job["job_name"] == job_name:
                return self.enqueued_jobs.pop(index)["payload"]
        return None

    def ping(self) -> bool:
        return True
