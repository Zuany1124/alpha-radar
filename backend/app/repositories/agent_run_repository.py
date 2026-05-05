from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.agent_run import AgentRun


class AgentRunRepository:
    """AgentRun 轻量审计查询仓储。"""

    def __init__(self, db: Session) -> None:
        self.db = db

    def list(
        self,
        limit: int = 50,
        offset: int = 0,
        workflow_name: str | None = None,
        agent_name: str | None = None,
        status: str | None = None,
    ) -> list[AgentRun]:
        """分页查询 AgentRun，可按工作流、Agent 名称和状态过滤。"""

        stmt = select(AgentRun)
        if workflow_name is not None:
            stmt = stmt.where(AgentRun.workflow_name == workflow_name)
        if agent_name is not None:
            stmt = stmt.where(AgentRun.agent_name == agent_name)
        if status is not None:
            stmt = stmt.where(AgentRun.status == status)
        stmt = stmt.order_by(AgentRun.created_at.desc()).offset(offset).limit(limit)
        return list(self.db.scalars(stmt).all())

    def get(self, agent_run_id: str) -> AgentRun | None:
        """按 ID 查询单条 AgentRun。"""

        return self.db.get(AgentRun, agent_run_id)

    def get_many(self, agent_run_ids: list[str]) -> list[AgentRun]:
        """按 ID 列表批量查询 AgentRun，并保持输入顺序。"""

        if not agent_run_ids:
            return []
        items = list(
            self.db.scalars(select(AgentRun).where(AgentRun.id.in_(agent_run_ids))).all()
        )
        by_id = {item.id: item for item in items}
        return [by_id[agent_run_id] for agent_run_id in agent_run_ids if agent_run_id in by_id]
