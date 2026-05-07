from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.evidence_item import EvidenceItem
from app.models.mixins import now_utc
from app.schemas.evidence import EvidenceIngestDocument, EvidenceRetrievalQuery


class EvidenceRepository:
    """EvidenceItem 查询和写入仓储。"""

    def __init__(self, db: Session) -> None:
        self.db = db

    def list(
        self,
        limit: int = 50,
        offset: int = 0,
        evidence_type: str | None = None,
    ) -> list[EvidenceItem]:
        """分页查询 EvidenceItem，可按证据类型过滤。"""

        stmt = select(EvidenceItem)
        if evidence_type is not None:
            stmt = stmt.where(EvidenceItem.evidence_type == evidence_type)
        stmt = stmt.order_by(EvidenceItem.created_at.desc()).offset(offset).limit(limit)
        return list(self.db.scalars(stmt).all())

    def get(self, evidence_id: str) -> EvidenceItem | None:
        """按 ID 查询单条 EvidenceItem。"""

        return self.db.get(EvidenceItem, evidence_id)

    def get_by_source_url(self, source_url: str) -> EvidenceItem | None:
        """按 source URL 查询 EvidenceItem。"""

        return self.db.scalar(select(EvidenceItem).where(EvidenceItem.source_url == source_url))

    def get_many(self, evidence_ids: list[str]) -> list[EvidenceItem]:
        """按 ID 列表批量查询 EvidenceItem，并保持输入顺序。"""

        if not evidence_ids:
            return []
        items = list(
            self.db.scalars(select(EvidenceItem).where(EvidenceItem.id.in_(evidence_ids))).all()
        )
        by_id = {item.id: item for item in items}
        return [by_id[evidence_id] for evidence_id in evidence_ids if evidence_id in by_id]

    def upsert_document(
        self,
        document: EvidenceIngestDocument,
        embedding: list[float] | None,
    ) -> EvidenceItem:
        """写入或更新 EvidenceItem。"""

        evidence = self.get_by_source_url(document.source_url) if document.source_url else None
        if evidence is None:
            evidence = EvidenceItem(evidence_type=document.evidence_type, title=document.title)
            self.db.add(evidence)

        evidence.evidence_type = document.evidence_type
        evidence.title = document.title
        evidence.source_url = document.source_url
        evidence.published_at = document.published_at
        evidence.fetched_at = document.fetched_at or now_utc()
        evidence.summary = document.summary
        evidence.evidence_metadata = document.evidence_metadata
        evidence.embedding = embedding
        self.db.flush()
        return evidence

    def search_keyword(self, query: EvidenceRetrievalQuery) -> list[EvidenceItem]:
        """使用数据库字段做轻量关键词检索。"""

        terms = [term.lower() for term in query.query.split() if term.strip()]
        stmt = select(EvidenceItem).order_by(EvidenceItem.created_at.desc())
        if query.evidence_types:
            stmt = stmt.where(EvidenceItem.evidence_type.in_(query.evidence_types))

        candidates = list(self.db.scalars(stmt).all())
        matched: list[EvidenceItem] = []
        for item in candidates:
            if not self._matches_metadata(item, query):
                continue
            text = f"{item.title} {item.summary or ''} {item.source_url or ''}".lower()
            if not terms or any(term in text for term in terms):
                matched.append(item)
            if len(matched) >= query.limit:
                break
        return matched

    def search_vector(
        self,
        query: EvidenceRetrievalQuery,
        embedding: list[float] | None,
    ) -> list[EvidenceItem]:
        """使用内存余弦相似度作为 pgvector 测试 fallback。"""

        if not embedding:
            return []

        candidates = [
            item
            for item in self.db.scalars(select(EvidenceItem)).all()
            if item.embedding and self._matches_metadata(item, query)
        ]
        scored = sorted(
            candidates,
            key=lambda item: self._cosine_similarity(embedding, item.embedding or []),
            reverse=True,
        )
        return scored[: query.limit]

    @staticmethod
    def _matches_metadata(item: EvidenceItem, query: EvidenceRetrievalQuery) -> bool:
        metadata = item.evidence_metadata or {}
        if query.asset_symbol and metadata.get("asset_symbol") != query.asset_symbol:
            return False
        if query.asset_mint and metadata.get("asset_mint") != query.asset_mint:
            return False
        return True

    @staticmethod
    def _cosine_similarity(left: list[float], right: list[float]) -> float:
        if not left or not right:
            return 0.0
        size = min(len(left), len(right))
        dot = sum(left[index] * right[index] for index in range(size))
        left_norm = sum(left[index] ** 2 for index in range(size)) ** 0.5
        right_norm = sum(right[index] ** 2 for index in range(size)) ** 0.5
        if left_norm == 0 or right_norm == 0:
            return 0.0
        return dot / (left_norm * right_norm)
