from __future__ import annotations

import json
from urllib.parse import urlencode
import urllib.request


class HeliusClientError(RuntimeError):
    """Helius 请求失败。"""


class HeliusClient:
    """最小 Helius Wallet API 客户端。"""

    def __init__(self, api_key: str, base_url: str = "https://api.helius.xyz", timeout_seconds: int = 10) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def get_wallet_history(self, address: str, cursor: str | None = None, limit: int = 100) -> dict:
        params = {"limit": limit}
        if cursor:
            params["before"] = cursor
        params["tokenAccounts"] = "balanceChanged"
        return self._get_json(f"/v1/wallet/{address}/history", params)

    def get_wallet_transfers(self, address: str, limit: int = 100) -> dict:
        params = {"limit": limit}
        return self._get_json(f"/v1/wallet/{address}/transfers", params)

    def _get_json(self, path: str, params: dict) -> dict:
        query = urlencode(params)
        url = f"{self.base_url}{path}?{query}"
        request = urllib.request.Request(url, headers={"X-Api-Key": self.api_key, "Accept": "application/json"})

        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as exc:  # pragma: no cover - urllib wraps transport errors variably
            raise HeliusClientError(f"Helius request failed for {path}: {exc}") from exc
