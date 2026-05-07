from sqlalchemy.orm import Session

from app.models.agent_run import AgentRun
from app.models.asset import Asset
from app.models.lead import Lead
from app.models.mixins import now_utc
from app.models.signal_event import SignalEvent
from app.models.wallet import Wallet
from app.repositories.agent_run_repository import AgentRunRepository
from app.repositories.evidence_repository import EvidenceRepository
from app.repositories.lead_repository import LeadRepository
from app.schemas.evidence import EvidenceRetrievalQuery
from app.services.evidence_service import EvidenceService
from app.workers.workflows.lead_analysis.schemas import (
    OnchainSignalOutput,
    RagResearchOutput,
    RiskAssessmentOutput,
    SynthesizedLeadOutput,
)
from app.workers.workflows.lead_analysis.state import LeadAnalysisState


def load_signal_context(state: LeadAnalysisState, db: Session | None = None) -> dict:
    if db is None:
        return {
            "signal_context": {
                "scan_id": state["scan_id"],
                "signal_event_ids": state.get("signal_event_ids", []),
            }
        }

    signal_events = [
        event
        for event_id in state.get("signal_event_ids", [])
        if (event := db.get(SignalEvent, event_id)) is not None
    ]
    events = []
    for event in signal_events:
        asset = db.get(Asset, event.asset_id) if event.asset_id else None
        wallet = db.get(Wallet, event.wallet_id) if event.wallet_id else None
        events.append(
            {
                "id": event.id,
                "asset_id": event.asset_id,
                "asset_symbol": asset.symbol if asset else None,
                "asset_mint": asset.mint_address if asset else None,
                "wallet_id": event.wallet_id,
                "wallet_address": wallet.address if wallet else None,
                "event_type": event.event_type,
                "anomaly_score": event.anomaly_score,
                "event_timestamp": event.event_timestamp.isoformat(),
                "raw_payload": event.raw_payload,
            }
        )
    return {
        "signal_context": {
            "scan_id": state["scan_id"],
            "signal_event_ids": state.get("signal_event_ids", []),
            "events": events,
        }
    }


def onchain_signal_agent(state: LeadAnalysisState) -> dict:
    events = state.get("signal_context", {}).get("events") or []
    if not events:
        return {
            "onchain_signal": {
                "summary": "On-chain signal analysis placeholder",
                "signal_event_ids": state.get("signal_event_ids", []),
            }
        }
    primary = max(events, key=lambda event: event.get("anomaly_score") or 0)
    asset_label = primary.get("asset_symbol") or primary.get("asset_mint") or "unknown asset"
    output = OnchainSignalOutput(
        summary=(
            f"{asset_label} {primary.get('event_type')} reached anomaly score "
            f"{primary.get('anomaly_score') or 0:.2f} for a monitored wallet."
        ),
        signal_event_ids=[event["id"] for event in events],
        asset_id=primary.get("asset_id"),
        asset_symbol=primary.get("asset_symbol"),
        primary_wallet_id=primary.get("wallet_id"),
        event_type=primary.get("event_type"),
        anomaly_score=primary.get("anomaly_score"),
    )
    return {
        "onchain_signal": output.model_dump()
    }


def market_context_agent(state: LeadAnalysisState) -> dict:
    return {"market_context": {"summary": "Market context placeholder", "data_status": "not_connected"}}


def rag_research_agent(
    state: LeadAnalysisState,
    db: Session | None = None,
    evidence_service: EvidenceService | None = None,
) -> dict:
    if db is None:
        return {"rag_research": {"summary": "RAG research placeholder", "evidence_ids": []}}

    onchain = state.get("onchain_signal", {})
    asset_symbol = onchain.get("asset_symbol")
    query_text = " ".join(
        part
        for part in [
            asset_symbol or "",
            onchain.get("event_type") or "",
            "liquidity volume project news",
        ]
        if part
    )
    service = evidence_service or EvidenceService(EvidenceRepository(db))
    results = service.retrieve_evidence(EvidenceRetrievalQuery(query=query_text, asset_symbol=asset_symbol, limit=5))
    evidence_ids = [result.evidence.id for result in results]
    if evidence_ids:
        summary = f"Retrieved {len(evidence_ids)} evidence item(s) for {asset_symbol or 'asset'}."
    else:
        summary = f"No evidence found for {asset_symbol or 'asset'}."
    return {"rag_research": RagResearchOutput(summary=summary, evidence_ids=evidence_ids).model_dump()}


def risk_skeptic_agent(state: LeadAnalysisState) -> dict:
    evidence_ids = state.get("rag_research", {}).get("evidence_ids", [])
    anomaly_score = state.get("onchain_signal", {}).get("anomaly_score") or 0
    if not evidence_ids:
        output = RiskAssessmentOutput(
            summary="Evidence is missing; treat this as a low-confidence research lead.",
            risk_level="high",
        )
    elif anomaly_score >= 0.85:
        output = RiskAssessmentOutput(
            summary="High anomaly score is supported by retrieved evidence; still verify liquidity and freshness.",
            risk_level="medium",
        )
    else:
        output = RiskAssessmentOutput(
            summary="Evidence exists, but anomaly strength is moderate.",
            risk_level="medium",
        )
    return {"risk_assessment": output.model_dump()}


def lead_synthesizer(state: LeadAnalysisState) -> dict:
    onchain = state.get("onchain_signal", {})
    if not onchain.get("asset_symbol"):
        return {
            "lead": {
                "title": "Research lead skeleton",
                "signal_summary": state["onchain_signal"]["summary"],
                "why_this_matters": "Placeholder lead pending real Helius, market, and RAG inputs.",
                "risk_notes": state["risk_assessment"]["summary"],
                "confidence": 0.0,
                "agent_verdict": "needs_real_analysis",
            },
            "workflow_status": "succeeded",
        }

    evidence_ids = state.get("rag_research", {}).get("evidence_ids", [])
    risk = state.get("risk_assessment", {})
    confidence = 0.78 if evidence_ids else 0.35
    if risk.get("risk_level") == "high":
        confidence = min(confidence, 0.4)
    output = SynthesizedLeadOutput(
        title=f"{onchain['asset_symbol']} {onchain.get('event_type')} signal from monitored wallet",
        signal_summary=onchain["summary"],
        why_this_matters=(
            "A monitored wallet produced a high-score signal that may point to fresh asset activity."
        ),
        risk_notes=risk.get("summary", "Risk review unavailable."),
        confidence=confidence,
        agent_verdict="research" if evidence_ids else "needs_more_evidence",
        asset_id=onchain.get("asset_id"),
        primary_wallet_id=onchain.get("primary_wallet_id"),
        related_signal_event_ids=onchain.get("signal_event_ids", []),
        related_evidence_ids=evidence_ids,
    )
    return {
        "lead": output.model_dump(),
        "workflow_status": "succeeded",
    }


def persist_agent_run(state: LeadAnalysisState, db: Session | None = None) -> dict:
    agent_run_payload = {
        "workflow_name": "lead_analysis",
        "agent_name": "lead_synthesizer",
        "model": "deterministic-fixture",
        "input_payload": {
            "scan_id": state["scan_id"],
            "signal_event_ids": state.get("signal_event_ids", []),
        },
        "output_payload": {"lead": state["lead"]},
        "status": state["workflow_status"],
        "langsmith_project": None,
        "langsmith_trace_id": None,
        "langsmith_run_url": None,
    }
    if db is None:
        return {"agent_run": agent_run_payload}

    timestamp = now_utc()
    agent_run = AgentRun(
        **agent_run_payload,
        started_at=timestamp,
        finished_at=timestamp,
        token_usage={},
        trace_tags=["lead_analysis"],
        trace_metadata={
            "scan_id": state["scan_id"],
            "signal_event_ids": state.get("signal_event_ids", []),
            "workflow_name": "lead_analysis",
        },
    )
    AgentRunRepository(db).create(agent_run)

    lead_payload = state["lead"]
    lead = Lead(
        title=lead_payload["title"],
        asset_id=lead_payload.get("asset_id"),
        primary_wallet_id=lead_payload.get("primary_wallet_id"),
        signal_summary=lead_payload["signal_summary"],
        why_this_matters=lead_payload.get("why_this_matters"),
        risk_notes=lead_payload.get("risk_notes"),
        confidence=lead_payload.get("confidence"),
        freshness_timestamp=timestamp,
        agent_verdict=lead_payload.get("agent_verdict"),
        related_signal_event_ids=lead_payload.get("related_signal_event_ids", []),
        related_evidence_ids=lead_payload.get("related_evidence_ids", []),
        related_agent_run_ids=[agent_run.id],
    )
    LeadRepository(db).create(lead)
    db.commit()

    lead_payload = {**lead_payload, "id": lead.id, "related_agent_run_ids": [agent_run.id]}
    agent_run_payload = {**agent_run_payload, "id": agent_run.id}
    return {"lead": lead_payload, "agent_run": agent_run_payload}
