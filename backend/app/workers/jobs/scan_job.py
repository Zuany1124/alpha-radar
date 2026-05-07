from decimal import Decimal
from typing import Any

from app.core.config import get_settings
from app.db.session import SessionLocal
from app.models.signal_event import SignalEvent
from app.repositories.asset_repository import AssetRepository
from app.repositories.candidate_wallet_repository import CandidateWalletRepository
from app.repositories.evidence_repository import EvidenceRepository
from app.repositories.scan_repository import ScanRepository
from app.repositories.signal_event_repository import SignalEventRepository
from app.repositories.wallet_repository import WalletRepository
from app.services.evidence_service import build_evidence_service
from app.workers.integrations.helius_client import HeliusClient
from app.workers.integrations.providers import FixtureProvider, HeliusProvider, SolanaActivityProvider
from app.workers.integrations.scoring import score_signal_events
from app.workers.integrations.tools import (
    fetch_wallet_history,
    fetch_wallet_transfers,
    normalize_signal_events,
    recommend_candidate_wallets,
)
from app.workers.workflows.lead_analysis.graph import build_lead_analysis_graph


def run_scan_job(scan_id: str, db_session=None, settings: Any | None = None) -> dict:
    settings = settings or get_settings()
    db = db_session or SessionLocal()
    owns_session = db_session is None
    try:
        scans = ScanRepository(db)
        wallets = WalletRepository(db)
        assets = AssetRepository(db)
        signal_events = SignalEventRepository(db)
        candidates = CandidateWalletRepository(db)

        scan = scans.get(scan_id)
        if scan is None:
            raise ValueError(f"Scan not found: {scan_id}")

        provider = _build_provider(settings)
        target_wallet_ids = scan.scope.get("wallet_ids") or None
        target_wallets = wallets.list_active(wallet_ids=target_wallet_ids)

        normalized_events = []
        for wallet in target_wallets:
            history_page = fetch_wallet_history(
                provider=provider,
                address=wallet.address,
                limit=settings.signal_history_limit,
            )
            transfers = fetch_wallet_transfers(
                provider=provider,
                address=wallet.address,
                limit=settings.signal_transfers_limit,
            )
            normalized_events.extend(
                normalize_signal_events(
                    wallet=wallet,
                    history_page=history_page,
                    transfers=transfers,
                    scan_id=scan_id,
                )
            )

        scored_events = score_signal_events(normalized_events)
        persisted_events = signal_events.create_many(
            [_build_signal_event_model(item, assets) for item in scored_events]
        )

        threshold_signal_ids = [
            item.id
            for item in persisted_events
            if item.anomaly_score is not None and item.anomaly_score >= settings.signal_anomaly_threshold
        ]

        event_lookup = {event.raw_payload.get("signature"): event for event in persisted_events}
        for recommendation in recommend_candidate_wallets(scored_events, threshold=settings.signal_anomaly_threshold):
            if wallets.get_by_address(recommendation.address) is not None:
                continue
            candidates.upsert_pending(
                address=recommendation.address,
                recommendation_reason=recommendation.recommendation_reason,
                related_wallet_ids=recommendation.related_wallet_ids,
                evidence_ids=recommendation.evidence_ids,
            )

        db.commit()

        evidence_service = build_evidence_service(settings, EvidenceRepository(db))
        evidence_service.ingest_fixture_file(
            getattr(settings, "evidence_fixture_path", "tests/fixtures/evidence_fixture.json")
        )

        graph = build_lead_analysis_graph(db_session=db, evidence_service=evidence_service)
        raw_result = graph.invoke({"scan_id": scan_id, "signal_event_ids": threshold_signal_ids})
        created_lead_count = 1 if threshold_signal_ids and raw_result.get("workflow_status") == "succeeded" else 0

        return {
            "status": raw_result.get("workflow_status", "succeeded"),
            "created_signal_event_count": len(persisted_events),
            "created_lead_count": created_lead_count,
            "raw_result": raw_result,
            "signal_event_ids": threshold_signal_ids,
            "event_signatures": sorted(event_lookup.keys()),
        }
    finally:
        if owns_session:
            db.close()


def _build_provider(settings) -> SolanaActivityProvider:
    if settings.signal_provider == "fixture":
        return FixtureProvider(settings.signal_fixture_path)
    if settings.signal_provider == "helius":
        if not settings.helius_api_key:
            raise ValueError("HELIUS_API_KEY is required when signal_provider=helius")
        return HeliusProvider(HeliusClient(api_key=settings.helius_api_key))
    if settings.helius_api_key:
        return HeliusProvider(HeliusClient(api_key=settings.helius_api_key))
    return FixtureProvider(settings.signal_fixture_path)


def _build_signal_event_model(item, assets: AssetRepository) -> SignalEvent:
    asset_id = None
    if item.asset_mint:
        asset = assets.get_or_create_by_mint(
            mint_address=item.asset_mint,
            symbol=item.asset_symbol,
            name=item.asset_name,
            decimals=item.asset_decimals,
            asset_metadata={"provider": item.raw_provider},
        )
        asset_id = asset.id

    return SignalEvent(
        wallet_id=item.wallet_id,
        asset_id=asset_id,
        event_type=item.event_type,
        event_timestamp=item.event_timestamp,
        amount=item.amount if isinstance(item.amount, Decimal) else None,
        usd_value=item.usd_value if isinstance(item.usd_value, Decimal) else None,
        counterparty=item.counterparty,
        raw_provider=item.raw_provider,
        raw_payload=item.raw_payload,
        anomaly_score=item.anomaly_score,
        scan_id=item.scan_id,
    )
