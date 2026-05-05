from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class EvidenceRead(BaseModel):
    """EvidenceItem API 读取响应。"""

    id: str
    evidence_type: str
    title: str
    source_url: str | None
    published_at: datetime | None
    fetched_at: datetime | None
    summary: str | None
    evidence_metadata: dict = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EvidenceList(BaseModel):
    """EvidenceItem 列表响应。"""

    items: list[EvidenceRead] = Field(default_factory=list)
