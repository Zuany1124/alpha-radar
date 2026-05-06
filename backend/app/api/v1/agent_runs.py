from fastapi import APIRouter, Depends

from app.api.deps import get_agent_run_service
from app.schemas.agent_run import AgentRunList, AgentRunRead
from app.services.agent_run_service import AgentRunService

router = APIRouter()


@router.get("", response_model=AgentRunList)
def list_agent_runs(
    limit: int = 50,
    offset: int = 0,
    workflow_name: str | None = None,
    agent_name: str | None = None,
    status: str | None = None,
    service: AgentRunService = Depends(get_agent_run_service),
) -> AgentRunList:
    """查询 AgentRun 列表。"""

    return AgentRunList(
        items=service.list_agent_runs(
            limit=limit,
            offset=offset,
            workflow_name=workflow_name,
            agent_name=agent_name,
            run_status=status,
        )
    )


@router.get("/{agent_run_id}", response_model=AgentRunRead)
def get_agent_run(
    agent_run_id: str,
    service: AgentRunService = Depends(get_agent_run_service),
):
    """查询 AgentRun 详情。"""

    return service.get_agent_run(agent_run_id)
