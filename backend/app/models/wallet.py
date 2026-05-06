from sqlalchemy import Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import IdMixin, TimestampMixin


class Wallet(IdMixin, TimestampMixin, Base):
    __tablename__ = "wallets"

    address: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    label: Mapped[str | None] = mapped_column(String(160))
    notes: Mapped[str | None] = mapped_column(Text)
    source: Mapped[str | None] = mapped_column(String(80))
    confidence: Mapped[float | None] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(32), default="active", nullable=False)
