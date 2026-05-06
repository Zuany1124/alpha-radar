from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol

from app.workers.integrations.helius_client import HeliusClient


ProviderHistoryPage = dict
ProviderTransfersPayload = dict


class SolanaActivityProvider(Protocol):
    provider_name: str

    def fetch_wallet_history(
        self,
        address: str,
        cursor: str | None = None,
        limit: int = 100,
    ) -> ProviderHistoryPage:
        ...

    def fetch_wallet_transfers(self, address: str, limit: int = 100) -> ProviderTransfersPayload:
        ...


class HeliusProvider:
    provider_name = "helius"

    def __init__(self, client: HeliusClient) -> None:
        self.client = client

    def fetch_wallet_history(
        self,
        address: str,
        cursor: str | None = None,
        limit: int = 100,
    ) -> ProviderHistoryPage:
        payload = self.client.get_wallet_history(address=address, cursor=cursor, limit=limit)
        return {**payload, "_provider": self.provider_name}

    def fetch_wallet_transfers(self, address: str, limit: int = 100) -> ProviderTransfersPayload:
        payload = self.client.get_wallet_transfers(address=address, limit=limit)
        return {**payload, "_provider": self.provider_name}


class FixtureProvider:
    provider_name = "fixture"

    def __init__(self, fixture_path: str | Path) -> None:
        self.fixture_path = Path(fixture_path)
        self.fixture = json.loads(self.fixture_path.read_text(encoding="utf-8"))

    def fetch_wallet_history(
        self,
        address: str,
        cursor: str | None = None,
        limit: int = 100,
    ) -> ProviderHistoryPage:
        wallet_fixture = self.fixture.get("wallets", {}).get(address, {})
        payload = wallet_fixture.get(
            "history",
            {"transactions": [], "pagination": {"nextCursor": None, "hasMore": False}},
        )
        return {**payload, "_provider": self.provider_name}

    def fetch_wallet_transfers(self, address: str, limit: int = 100) -> ProviderTransfersPayload:
        wallet_fixture = self.fixture.get("wallets", {}).get(address, {})
        payload = wallet_fixture.get("transfers", {"data": []})
        return {**payload, "_provider": self.provider_name}
