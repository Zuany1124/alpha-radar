from pydantic import BaseModel, Field


class LeadAnalysisInput(BaseModel):
    scan_id: str
    signal_event_ids: list[str] = Field(default_factory=list)


class SkeletonLeadOutput(BaseModel):
    title: str
    signal_summary: str
    why_this_matters: str
    risk_notes: str
    confidence: float
    agent_verdict: str
