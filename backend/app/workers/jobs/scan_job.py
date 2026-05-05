from app.workers.workflows.lead_analysis.graph import build_lead_analysis_graph


def run_scan_job(scan_id: str) -> dict:
    graph = build_lead_analysis_graph()
    raw_result = graph.invoke({"scan_id": scan_id, "signal_event_ids": []})
    return {
        "status": raw_result.get("workflow_status", "succeeded"),
        "created_signal_event_count": 0,
        "created_lead_count": 0,
        "raw_result": raw_result,
    }
