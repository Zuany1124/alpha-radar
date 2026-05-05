from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.lead import Lead


class LeadRepository:
    """Lead 只读查询仓储。"""

    def __init__(self, db: Session) -> None:
        self.db = db

    def list(
        self,
        limit: int = 50,
        offset: int = 0,
        asset_id: str | None = None,
        primary_wallet_id: str | None = None,
        agent_verdict: str | None = None,
        min_confidence: float | None = None,
    ) -> list[Lead]:
        """分页查询 Lead，可按资产、钱包、结论和最低置信度过滤。"""

        stmt = select(Lead)
        if asset_id is not None:
            stmt = stmt.where(Lead.asset_id == asset_id)
        if primary_wallet_id is not None:
            stmt = stmt.where(Lead.primary_wallet_id == primary_wallet_id)
        if agent_verdict is not None:
            stmt = stmt.where(Lead.agent_verdict == agent_verdict)
        if min_confidence is not None:
            stmt = stmt.where(Lead.confidence >= min_confidence)
        stmt = stmt.order_by(Lead.created_at.desc()).offset(offset).limit(limit)
        return list(self.db.scalars(stmt).all())

    def get(self, lead_id: str) -> Lead | None:
        """按 ID 查询单条 Lead。"""

        return self.db.get(Lead, lead_id)
