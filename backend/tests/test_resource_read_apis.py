from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.agent_run import AgentRun
from app.models.asset import Asset
from app.models.evidence_item import EvidenceItem
from app.models.lead import Lead
from app.models.wallet import Wallet


def test_lead_list_returns_persisted_leads(client: TestClient, db_session: Session) -> None:
    wallet = Wallet(address="wallet-1", label="Seed wallet", status="active")
    asset = Asset(mint_address="asset-1", symbol="BONK", name="Bonk", decimals=5)
    db_session.add_all([wallet, asset])
    db_session.flush()
    lead = Lead(
        title="Wallet accumulation lead",
        asset_id=asset.id,
        primary_wallet_id=wallet.id,
        signal_summary="Seed wallet increased BONK exposure.",
        why_this_matters="Repeated accumulation from a monitored wallet.",
        risk_notes="Liquidity needs review.",
        confidence=0.72,
        freshness_timestamp=datetime(2026, 5, 5, tzinfo=timezone.utc),
        agent_verdict="research",
        related_signal_event_ids=["signal-1"],
        related_evidence_ids=[],
        related_agent_run_ids=[],
    )
    db_session.add(lead)
    db_session.commit()

    response = client.get("/api/v1/leads")

    assert response.status_code == 200
    item = response.json()["items"][0]
    assert item["id"] == lead.id
    assert item["title"] == "Wallet accumulation lead"
    assert item["asset_id"] == asset.id
    assert item["primary_wallet_id"] == wallet.id
    assert item["signal_summary"] == "Seed wallet increased BONK exposure."
    assert item["why_this_matters"] == "Repeated accumulation from a monitored wallet."
    assert item["risk_notes"] == "Liquidity needs review."
    assert item["confidence"] == 0.72
    assert item["freshness_timestamp"] == "2026-05-05T00:00:00Z"
    assert item["agent_verdict"] == "research"
    assert item["related_signal_event_ids"] == ["signal-1"]
    assert item["related_evidence_ids"] == []
    assert item["related_agent_run_ids"] == []
    assert item["created_at"]
    assert item["updated_at"]


def test_lead_detail_expands_related_evidence_and_agent_runs(
    client: TestClient, db_session: Session
) -> None:
    evidence = EvidenceItem(
        evidence_type="news",
        title="Project update",
        source_url="https://example.com/update",
        published_at=datetime(2026, 5, 4, tzinfo=timezone.utc),
        fetched_at=datetime(2026, 5, 5, tzinfo=timezone.utc),
        summary="Project shipped a new integration.",
        evidence_metadata={"source": "fixture"},
        embedding=[0.1, 0.2],
    )
    agent_run = AgentRun(
        workflow_name="lead_analysis",
        agent_name="lead_synthesizer",
        model="fixture-model",
        input_payload={"signal_event_ids": ["signal-1"]},
        output_payload={"verdict": "research"},
        status="succeeded",
        started_at=datetime(2026, 5, 5, 1, tzinfo=timezone.utc),
        finished_at=datetime(2026, 5, 5, 1, 0, 2, tzinfo=timezone.utc),
        token_usage={"total_tokens": 42},
        langsmith_project="alpharadar",
        langsmith_trace_id="trace-1",
        langsmith_run_url="https://smith.langchain.com/r/trace-1",
        trace_tags=["fixture"],
        trace_metadata={"scan_id": "scan-1"},
    )
    db_session.add_all([evidence, agent_run])
    db_session.flush()
    lead = Lead(
        title="Detailed lead",
        signal_summary="Signal with expanded audit trail.",
        related_signal_event_ids=["signal-1"],
        related_evidence_ids=[evidence.id],
        related_agent_run_ids=[agent_run.id],
    )
    db_session.add(lead)
    db_session.commit()

    response = client.get(f"/api/v1/leads/{lead.id}")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == lead.id
    assert body["evidence_items"][0]["id"] == evidence.id
    assert body["evidence_items"][0]["evidence_metadata"] == {"source": "fixture"}
    assert "embedding" not in body["evidence_items"][0]
    assert body["agent_runs"][0]["id"] == agent_run.id
    assert body["agent_runs"][0]["token_usage"] == {"total_tokens": 42}
    assert body["agent_runs"][0]["trace_metadata"] == {"scan_id": "scan-1"}


def test_evidence_read_apis_do_not_expose_embedding(
    client: TestClient, db_session: Session
) -> None:
    evidence = EvidenceItem(
        evidence_type="market",
        title="Market context",
        summary="Volume increased.",
        evidence_metadata={"asset": "BONK"},
        embedding=[0.3, 0.4],
    )
    db_session.add(evidence)
    db_session.commit()

    list_response = client.get("/api/v1/evidence")
    detail_response = client.get(f"/api/v1/evidence/{evidence.id}")

    assert list_response.status_code == 200
    assert list_response.json()["items"][0]["id"] == evidence.id
    assert "embedding" not in list_response.json()["items"][0]
    assert detail_response.status_code == 200
    assert detail_response.json()["evidence_metadata"] == {"asset": "BONK"}
    assert "embedding" not in detail_response.json()


def test_agent_run_read_apis_return_lightweight_audit_fields(
    client: TestClient, db_session: Session
) -> None:
    agent_run = AgentRun(
        workflow_name="lead_analysis",
        agent_name="risk_skeptic_agent",
        model="fixture-model",
        input_payload={"lead_id": "lead-1"},
        output_payload={"risk": "low_liquidity"},
        status="failed",
        error_message="fixture failure",
        token_usage={"prompt_tokens": 10},
        langsmith_project="alpharadar",
        langsmith_trace_id="trace-2",
        langsmith_run_url="https://smith.langchain.com/r/trace-2",
        trace_tags=["risk"],
        trace_metadata={"asset_id": "asset-1"},
    )
    db_session.add(agent_run)
    db_session.commit()

    list_response = client.get("/api/v1/agent-runs")
    detail_response = client.get(f"/api/v1/agent-runs/{agent_run.id}")

    assert list_response.status_code == 200
    assert list_response.json()["items"][0]["workflow_name"] == "lead_analysis"
    assert detail_response.status_code == 200
    assert detail_response.json()["input_payload"] == {"lead_id": "lead-1"}
    assert detail_response.json()["output_payload"] == {"risk": "low_liquidity"}
    assert detail_response.json()["error_message"] == "fixture failure"
    assert detail_response.json()["trace_tags"] == ["risk"]


def test_resource_read_apis_return_404_for_missing_records(client: TestClient) -> None:
    assert client.get("/api/v1/leads/missing").status_code == 404
    assert client.get("/api/v1/evidence/missing").status_code == 404
    assert client.get("/api/v1/agent-runs/missing").status_code == 404
