from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.evidence_item import EvidenceItem


class EvidenceIngestDocument(BaseModel):
    """Evidence ingestion 输入文档。"""

    evidence_type: str
    title: str
    source_url: str | None = None
    published_at: datetime | None = None
    fetched_at: datetime | None = None
    summary: str | None = None
    evidence_metadata: dict = Field(default_factory=dict)


class EvidenceRetrievalQuery(BaseModel):
    """Evidence 检索请求。"""

    query: str
    asset_symbol: str | None = None
    asset_mint: str | None = None
    evidence_types: list[str] = Field(default_factory=list)
    limit: int = 5


class EvidenceRetrievalResult(BaseModel):
    """Evidence 检索结果。"""

    evidence: EvidenceItem
    score: float
    match_source: str

    model_config = ConfigDict(arbitrary_types_allowed=True)


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
