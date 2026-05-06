from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AgentRunRead(BaseModel):
    """AgentRun 轻量审计读取响应。"""

    id: str
    workflow_name: str
    agent_name: str | None
    model: str | None
    input_payload: dict = Field(default_factory=dict)
    output_payload: dict = Field(default_factory=dict)
    status: str
    started_at: datetime | None
    finished_at: datetime | None
    error_message: str | None
    token_usage: dict = Field(default_factory=dict)
    langsmith_project: str | None
    langsmith_trace_id: str | None
    langsmith_run_url: str | None
    trace_tags: list[str] = Field(default_factory=list)
    trace_metadata: dict = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AgentRunList(BaseModel):
    """AgentRun 列表响应。"""

    items: list[AgentRunRead] = Field(default_factory=list)
