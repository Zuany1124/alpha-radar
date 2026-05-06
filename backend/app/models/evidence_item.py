from datetime import datetime

from sqlalchemy import JSON, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import IdMixin, TimestampMixin


class EvidenceItem(IdMixin, TimestampMixin, Base):
    __tablename__ = "evidence_items"

    evidence_type: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    source_url: Mapped[str | None] = mapped_column(Text)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    fetched_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    summary: Mapped[str | None] = mapped_column(Text)
    evidence_metadata: Mapped[dict] = mapped_column("metadata", JSON, default=dict, nullable=False)
    embedding: Mapped[list[float] | None] = mapped_column(JSON)
