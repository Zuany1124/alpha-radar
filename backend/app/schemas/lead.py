from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.agent_run import AgentRunRead
from app.schemas.evidence import EvidenceRead


class LeadRead(BaseModel):
    """Lead 列表与基础详情读取响应。"""

    id: str
    title: str
    asset_id: str | None
    primary_wallet_id: str | None
    signal_summary: str
    why_this_matters: str | None
    risk_notes: str | None
    confidence: float | None
    freshness_timestamp: datetime | None
    agent_verdict: str | None
    related_signal_event_ids: list[str] = Field(default_factory=list)
    related_evidence_ids: list[str] = Field(default_factory=list)
    related_agent_run_ids: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LeadDetailRead(LeadRead):
    """Lead 详情响应，展开关联证据和 AgentRun。"""

    evidence_items: list[EvidenceRead] = Field(default_factory=list)
    agent_runs: list[AgentRunRead] = Field(default_factory=list)


class LeadList(BaseModel):
    """Lead 列表响应。"""

    items: list[LeadRead] = Field(default_factory=list)
