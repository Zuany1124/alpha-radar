from datetime import datetime

from sqlalchemy import JSON, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import IdMixin, TimestampMixin


class AgentRun(IdMixin, TimestampMixin, Base):
    __tablename__ = "agent_runs"

    workflow_name: Mapped[str] = mapped_column(String(120), nullable=False)
    agent_name: Mapped[str | None] = mapped_column(String(120))
    model: Mapped[str | None] = mapped_column(String(120))
    input_payload: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    output_payload: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error_message: Mapped[str | None] = mapped_column(Text)
    token_usage: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    langsmith_project: Mapped[str | None] = mapped_column(String(160))
    langsmith_trace_id: Mapped[str | None] = mapped_column(String(160))
    langsmith_run_url: Mapped[str | None] = mapped_column(Text)
    trace_tags: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    trace_metadata: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
