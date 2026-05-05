from fastapi import HTTPException, status

from app.models.agent_run import AgentRun
from app.repositories.agent_run_repository import AgentRunRepository


class AgentRunService:
    """AgentRun 轻量审计查询服务。"""

    def __init__(self, agent_runs: AgentRunRepository) -> None:
        self.agent_runs = agent_runs

    def list_agent_runs(
        self,
        limit: int,
        offset: int,
        workflow_name: str | None = None,
        agent_name: str | None = None,
        run_status: str | None = None,
    ) -> list[AgentRun]:
        """分页查询 AgentRun 轻量审计记录。"""

        return self.agent_runs.list(
            limit=limit,
            offset=offset,
            workflow_name=workflow_name,
            agent_name=agent_name,
            status=run_status,
        )

    def get_agent_run(self, agent_run_id: str) -> AgentRun:
        """查询单条 AgentRun，不存在时返回 404。"""

        agent_run = self.agent_runs.get(agent_run_id)
        if agent_run is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent run not found")
        return agent_run
