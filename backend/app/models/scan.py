from datetime import datetime

from sqlalchemy import JSON, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import IdMixin, TimestampMixin


class Scan(IdMixin, TimestampMixin, Base):
    __tablename__ = "scans"

    trigger: Mapped[str] = mapped_column(String(32), nullable=False)
    scope: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="queued", nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error_message: Mapped[str | None] = mapped_column(Text)
    created_signal_event_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_lead_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
