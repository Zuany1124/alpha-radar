from app.workers.workflows.lead_analysis.graph import build_lead_analysis_graph


def test_lead_analysis_graph_invokes_deterministic_skeleton() -> None:
    graph = build_lead_analysis_graph()

    result = graph.invoke({"scan_id": "scan-1", "signal_event_ids": ["signal-1"]})

    assert result["scan_id"] == "scan-1"
    assert result["workflow_status"] == "succeeded"
    assert result["lead"]["title"] == "Research lead skeleton"
    assert result["agent_run"]["workflow_name"] == "lead_analysis"
    assert result["agent_run"]["status"] == "succeeded"
