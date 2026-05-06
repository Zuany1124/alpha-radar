from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.wallet import WalletRead


class CandidateWalletRead(BaseModel):
    id: str
    address: str
    recommendation_reason: str
    related_wallet_ids: list[str]
    evidence_ids: list[str]
    status: str
    reviewed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CandidateWalletList(BaseModel):
    items: list[CandidateWalletRead]


class CandidateWalletApproval(BaseModel):
    status: str
    wallet: WalletRead
