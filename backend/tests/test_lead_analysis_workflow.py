from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.asset import Asset
from app.models.evidence_item import EvidenceItem
from app.models.scan import Scan
from app.models.signal_event import SignalEvent
from app.models.wallet import Wallet
from app.workers.workflows.lead_analysis.graph import build_lead_analysis_graph


def test_lead_analysis_graph_invokes_deterministic_skeleton() -> None:
    graph = build_lead_analysis_graph()

    result = graph.invoke({"scan_id": "scan-1", "signal_event_ids": ["signal-1"]})

    assert result["scan_id"] == "scan-1"
    assert result["workflow_status"] == "succeeded"
    assert result["lead"]["title"] == "Research lead skeleton"
    assert result["agent_run"]["workflow_name"] == "lead_analysis"
    assert result["agent_run"]["status"] == "succeeded"


def test_lead_analysis_graph_persists_lead_and_agent_run_with_evidence(
    db_session: Session,
) -> None:
    wallet = Wallet(address="SeedWallet1111111111111111111111111111111111", status="active")
    asset = Asset(
        mint_address="MintAlpha111111111111111111111111111111111",
        symbol="ALPHA",
        name="Alpha Token",
        decimals=6,
    )
    scan = Scan(trigger="manual", scope={}, status="running")
    evidence = EvidenceItem(
        evidence_type="news",
        title="ALPHA liquidity program",
        summary="ALPHA announced a Solana liquidity program.",
        evidence_metadata={"asset_symbol": "ALPHA", "asset_mint": asset.mint_address},
        embedding=[1.0, 0.5, 0.25],
    )
    db_session.add_all([wallet, asset, scan, evidence])
    db_session.flush()
    signal = SignalEvent(
        wallet_id=wallet.id,
        asset_id=asset.id,
        event_type="transfer_in",
        event_timestamp=datetime(2026, 5, 6, tzinfo=timezone.utc),
        raw_provider="fixture",
        raw_payload={"signature": "sig-alpha"},
        anomaly_score=0.9,
        scan_id=scan.id,
    )
    db_session.add(signal)
    db_session.commit()

    graph = build_lead_analysis_graph(db_session=db_session)

    result = graph.invoke({"scan_id": scan.id, "signal_event_ids": [signal.id]})

    assert result["workflow_status"] == "succeeded"
    assert result["lead"]["related_signal_event_ids"] == [signal.id]
    assert result["lead"]["related_evidence_ids"] == [evidence.id]

    lead = db_session.query(__import__("app.models.lead", fromlist=["Lead"]).Lead).one()
    agent_run = db_session.query(__import__("app.models.agent_run", fromlist=["AgentRun"]).AgentRun).one()
    assert lead.title == "ALPHA transfer_in signal from monitored wallet"
    assert lead.related_signal_event_ids == [signal.id]
    assert lead.related_evidence_ids == [evidence.id]
    assert lead.related_agent_run_ids == [agent_run.id]
    assert agent_run.workflow_name == "lead_analysis"
    assert agent_run.status == "succeeded"
    assert agent_run.trace_metadata["scan_id"] == scan.id
