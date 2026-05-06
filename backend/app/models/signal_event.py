from datetime import datetime
from decimal import Decimal

from sqlalchemy import JSON, DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import IdMixin, TimestampMixin


class SignalEvent(IdMixin, TimestampMixin, Base):
    __tablename__ = "signal_events"

    wallet_id: Mapped[str | None] = mapped_column(ForeignKey("wallets.id"))
    asset_id: Mapped[str | None] = mapped_column(ForeignKey("assets.id"))
    event_type: Mapped[str] = mapped_column(String(80), nullable=False)
    event_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    amount: Mapped[Decimal | None] = mapped_column(Numeric(36, 12))
    usd_value: Mapped[Decimal | None] = mapped_column(Numeric(36, 6))
    counterparty: Mapped[str | None] = mapped_column(String(128))
    raw_provider: Mapped[str | None] = mapped_column(String(64))
    raw_payload: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    anomaly_score: Mapped[float | None]
    scan_id: Mapped[str | None] = mapped_column(ForeignKey("scans.id"))
