from langgraph.graph import END, START, StateGraph
from sqlalchemy.orm import Session

from app.services.evidence_service import EvidenceService
from app.workers.workflows.lead_analysis.nodes import (
    lead_synthesizer,
    load_signal_context,
    market_context_agent,
    onchain_signal_agent,
    persist_agent_run,
    rag_research_agent,
    risk_skeptic_agent,
)
from app.workers.workflows.lead_analysis.state import LeadAnalysisState


def build_lead_analysis_graph(
    db_session: Session | None = None,
    evidence_service: EvidenceService | None = None,
):
    builder = StateGraph(LeadAnalysisState)
    builder.add_node(
        "load_signal_context",
        lambda state: load_signal_context(state, db_session),
    )
    builder.add_node("onchain_signal_agent", onchain_signal_agent)
    builder.add_node("market_context_agent", market_context_agent)
    builder.add_node(
        "rag_research_agent",
        lambda state: rag_research_agent(state, db_session, evidence_service),
    )
    builder.add_node("risk_skeptic_agent", risk_skeptic_agent)
    builder.add_node("lead_synthesizer", lead_synthesizer)
    builder.add_node(
        "persist_agent_run",
        lambda state: persist_agent_run(state, db_session),
    )

    builder.add_edge(START, "load_signal_context")
    builder.add_edge("load_signal_context", "onchain_signal_agent")
    builder.add_edge("onchain_signal_agent", "market_context_agent")
    builder.add_edge("market_context_agent", "rag_research_agent")
    builder.add_edge("rag_research_agent", "risk_skeptic_agent")
    builder.add_edge("risk_skeptic_agent", "lead_synthesizer")
    builder.add_edge("lead_synthesizer", "persist_agent_run")
    builder.add_edge("persist_agent_run", END)

    return builder.compile()
