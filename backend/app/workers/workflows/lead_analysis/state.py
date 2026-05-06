from typing import TypedDict


class LeadAnalysisState(TypedDict, total=False):
    scan_id: str
    signal_event_ids: list[str]
    signal_context: dict
    onchain_signal: dict
    market_context: dict
    rag_research: dict
    risk_assessment: dict
    lead: dict
    agent_run: dict
    workflow_status: str
