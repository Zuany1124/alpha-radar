from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import IdMixin, TimestampMixin


class Lead(IdMixin, TimestampMixin, Base):
    __tablename__ = "leads"

    title: Mapped[str] = mapped_column(String(240), nullable=False)
    asset_id: Mapped[str | None] = mapped_column(ForeignKey("assets.id"))
    primary_wallet_id: Mapped[str | None] = mapped_column(ForeignKey("wallets.id"))
    signal_summary: Mapped[str] = mapped_column(Text, nullable=False)
    why_this_matters: Mapped[str | None] = mapped_column(Text)
    risk_notes: Mapped[str | None] = mapped_column(Text)
    confidence: Mapped[float | None] = mapped_column(Float)
    freshness_timestamp: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    agent_verdict: Mapped[str | None] = mapped_column(String(80))
    related_signal_event_ids: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    related_evidence_ids: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    related_agent_run_ids: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
