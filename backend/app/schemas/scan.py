from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ScanCreate(BaseModel):
    trigger: Literal["manual"] = "manual"
    scope: dict = Field(default_factory=dict)


class ScanRead(BaseModel):
    id: str
    trigger: str
    scope: dict
    status: str
    started_at: datetime | None
    finished_at: datetime | None
    error_message: str | None
    created_signal_event_count: int
    created_lead_count: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ScanList(BaseModel):
    items: list[ScanRead]
