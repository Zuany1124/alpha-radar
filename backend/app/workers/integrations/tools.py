from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal

from app.models.wallet import Wallet
from app.workers.integrations.providers import (
    ProviderHistoryPage,
    ProviderTransfersPayload,
    SolanaActivityProvider,
)


@dataclass(slots=True)
class NormalizedSignalEvent:
    wallet_id: str | None
    wallet_address: str
    asset_mint: str | None
    asset_symbol: str | None
    asset_name: str | None
    asset_decimals: int | None
    event_type: str
    event_timestamp: datetime
    amount: Decimal | None
    usd_value: Decimal | None
    counterparty: str | None
    raw_provider: str
    raw_payload: dict
    scan_id: str
    anomaly_score: float | None = None


@dataclass(slots=True)
class CandidateWalletRecommendation:
    address: str
    recommendation_reason: str
    related_wallet_ids: list[str]
    evidence_ids: list[str]


def fetch_wallet_history(
    provider: SolanaActivityProvider,
    address: str,
    cursor: str | None = None,
    limit: int = 100,
) -> ProviderHistoryPage:
    return provider.fetch_wallet_history(address=address, cursor=cursor, limit=limit)


def fetch_wallet_transfers(
    provider: SolanaActivityProvider,
    address: str,
    limit: int = 100,
) -> ProviderTransfersPayload:
    return provider.fetch_wallet_transfers(address=address, limit=limit)


def normalize_signal_events(
    wallet: Wallet,
    history_page: ProviderHistoryPage,
    transfers: ProviderTransfersPayload,
    scan_id: str,
) -> list[NormalizedSignalEvent]:
    raw_provider = history_page.get("_provider") or transfers.get("_provider") or "unknown"
    events: list[NormalizedSignalEvent] = []

    for transaction in history_page.get("transactions", []):
        for token_transfer in transaction.get("tokenTransfers", []):
            direction = _resolve_token_transfer_direction(wallet.address, token_transfer)
            if direction is None:
                continue
            events.append(
                NormalizedSignalEvent(
                    wallet_id=wallet.id,
                    wallet_address=wallet.address,
                    asset_mint=token_transfer.get("mint"),
                    asset_symbol=token_transfer.get("symbol"),
                    asset_name=token_transfer.get("name"),
                    asset_decimals=token_transfer.get("decimals"),
                    event_type=direction,
                    event_timestamp=_parse_timestamp(transaction.get("timestamp")),
                    amount=_to_decimal(token_transfer.get("tokenAmount")),
                    usd_value=_extract_usd_value(transaction),
                    counterparty=_extract_counterparty(wallet.address, token_transfer),
                    raw_provider=raw_provider,
                    raw_payload=transaction,
                    scan_id=scan_id,
                )
            )

    for transfer in transfers.get("data", []):
        direction = transfer.get("direction", "unknown")
        event_type = "transfer_in" if direction == "in" else "transfer_out"
        events.append(
            NormalizedSignalEvent(
                wallet_id=wallet.id,
                wallet_address=wallet.address,
                asset_mint=transfer.get("mint"),
                asset_symbol=transfer.get("symbol"),
                asset_name=transfer.get("name"),
                asset_decimals=transfer.get("decimals"),
                event_type=event_type,
                event_timestamp=_parse_timestamp(transfer.get("timestamp")),
                amount=_to_decimal(transfer.get("amount")),
                usd_value=_to_decimal(transfer.get("usdValue")),
                counterparty=transfer.get("counterparty"),
                raw_provider=raw_provider,
                raw_payload=transfer,
                scan_id=scan_id,
            )
        )

    return events


def recommend_candidate_wallets(
    events: list[NormalizedSignalEvent],
    threshold: float = 0.65,
) -> list[CandidateWalletRecommendation]:
    recommendations: dict[str, CandidateWalletRecommendation] = {}

    for event in sorted(events, key=lambda item: item.anomaly_score or 0, reverse=True):
        if not event.counterparty or (event.anomaly_score or 0) < threshold:
            continue
        if event.counterparty == event.wallet_address:
            continue
        reason = (
            f"{event.wallet_address} on {event.asset_symbol or event.asset_mint or 'unknown asset'} "
            f"showed {event.event_type} with anomaly score {event.anomaly_score:.2f}"
        )
        recommendations.setdefault(
            event.counterparty,
            CandidateWalletRecommendation(
                address=event.counterparty,
                recommendation_reason=reason,
                related_wallet_ids=[event.wallet_id] if event.wallet_id else [],
                evidence_ids=[],
            ),
        )

    return list(recommendations.values())


def _resolve_token_transfer_direction(wallet_address: str, token_transfer: dict) -> str | None:
    if token_transfer.get("toUserAccount") == wallet_address:
        return "swap_in"
    if token_transfer.get("fromUserAccount") == wallet_address:
        return "swap_out"
    return None


def _extract_counterparty(wallet_address: str, token_transfer: dict) -> str | None:
    if token_transfer.get("toUserAccount") == wallet_address:
        return token_transfer.get("fromUserAccount")
    if token_transfer.get("fromUserAccount") == wallet_address:
        return token_transfer.get("toUserAccount")
    return None


def _extract_usd_value(transaction: dict) -> Decimal | None:
    for transfer in transaction.get("tokenTransfers", []):
        usd_value = transfer.get("usdValue")
        if usd_value is not None:
            return _to_decimal(usd_value)
    return None


def _to_decimal(value: object) -> Decimal | None:
    if value is None:
        return None
    return Decimal(str(value))


def _parse_timestamp(value: object) -> datetime:
    if isinstance(value, int | float):
        return datetime.fromtimestamp(value, tz=UTC)
    if isinstance(value, str):
        normalized = value.replace("Z", "+00:00")
        return datetime.fromisoformat(normalized)
    return datetime.now(tz=UTC)
