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


class OnchainSignalOutput(BaseModel):
    """链上信号结构化摘要。"""

    summary: str
    signal_event_ids: list[str] = Field(default_factory=list)
    asset_id: str | None = None
    asset_symbol: str | None = None
    primary_wallet_id: str | None = None
    event_type: str | None = None
    anomaly_score: float | None = None


class RagResearchOutput(BaseModel):
    """RAG 检索结构化结果。"""

    summary: str
    evidence_ids: list[str] = Field(default_factory=list)


class RiskAssessmentOutput(BaseModel):
    """风险审查结构化结果。"""

    summary: str
    risk_level: str


class SynthesizedLeadOutput(BaseModel):
    """Lead Synthesizer 结构化输出。"""

    title: str
    signal_summary: str
    why_this_matters: str
    risk_notes: str
    confidence: float
    agent_verdict: str
    asset_id: str | None = None
    primary_wallet_id: str | None = None
    related_signal_event_ids: list[str] = Field(default_factory=list)
    related_evidence_ids: list[str] = Field(default_factory=list)
