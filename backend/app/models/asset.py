from sqlalchemy import JSON, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import IdMixin, TimestampMixin


class Asset(IdMixin, TimestampMixin, Base):
    __tablename__ = "assets"

    mint_address: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    symbol: Mapped[str | None] = mapped_column(String(32))
    name: Mapped[str | None] = mapped_column(String(160))
    decimals: Mapped[int | None] = mapped_column(Integer)
    asset_metadata: Mapped[dict] = mapped_column("metadata", JSON, default=dict, nullable=False)
