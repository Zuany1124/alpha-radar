from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class WalletCreate(BaseModel):
    address: str = Field(min_length=1, max_length=128)
    label: str | None = None
    notes: str | None = None
    source: str | None = None
    confidence: float | None = Field(default=None, ge=0, le=1)


class WalletUpdate(BaseModel):
    label: str | None = None
    notes: str | None = None
    source: str | None = None
    confidence: float | None = Field(default=None, ge=0, le=1)
    status: str | None = None


class WalletRead(BaseModel):
    id: str
    address: str
    label: str | None
    notes: str | None
    source: str | None
    confidence: float | None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WalletList(BaseModel):
    items: list[WalletRead]
