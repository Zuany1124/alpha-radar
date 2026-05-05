from datetime import datetime

from sqlalchemy import JSON, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import IdMixin, TimestampMixin


class CandidateWallet(IdMixin, TimestampMixin, Base):
    __tablename__ = "candidate_wallets"

    address: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    recommendation_reason: Mapped[str] = mapped_column(Text, nullable=False)
    related_wallet_ids: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    evidence_ids: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
