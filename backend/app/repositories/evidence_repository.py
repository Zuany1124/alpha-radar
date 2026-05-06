from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.evidence_item import EvidenceItem


class EvidenceRepository:
    """EvidenceItem 只读查询仓储。"""

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

    def get_many(self, evidence_ids: list[str]) -> list[EvidenceItem]:
        """按 ID 列表批量查询 EvidenceItem，并保持输入顺序。"""

        if not evidence_ids:
            return []
        items = list(
            self.db.scalars(select(EvidenceItem).where(EvidenceItem.id.in_(evidence_ids))).all()
        )
        by_id = {item.id: item for item in items}
        return [by_id[evidence_id] for evidence_id in evidence_ids if evidence_id in by_id]
