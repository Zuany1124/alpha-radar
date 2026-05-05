from app.workers.workflows.lead_analysis.state import LeadAnalysisState


def load_signal_context(state: LeadAnalysisState) -> dict:
    return {
        "signal_context": {
            "scan_id": state["scan_id"],
            "signal_event_ids": state.get("signal_event_ids", []),
        }
    }


def onchain_signal_agent(state: LeadAnalysisState) -> dict:
    return {
        "onchain_signal": {
            "summary": "On-chain signal analysis placeholder",
            "signal_event_ids": state.get("signal_event_ids", []),
        }
    }


def market_context_agent(state: LeadAnalysisState) -> dict:
    return {"market_context": {"summary": "Market context placeholder", "data_status": "not_connected"}}


def rag_research_agent(state: LeadAnalysisState) -> dict:
    return {"rag_research": {"summary": "RAG research placeholder", "evidence_ids": []}}


def risk_skeptic_agent(state: LeadAnalysisState) -> dict:
    return {"risk_assessment": {"summary": "Risk review placeholder", "risk_level": "unknown"}}


def lead_synthesizer(state: LeadAnalysisState) -> dict:
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


def persist_agent_run(state: LeadAnalysisState) -> dict:
    return {
        "agent_run": {
            "workflow_name": "lead_analysis",
            "agent_name": "lead_analysis_skeleton",
            "model": None,
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
    }
