from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.candidate_wallet import CandidateWallet


class CandidateWalletRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self, limit: int = 50, offset: int = 0) -> list[CandidateWallet]:
        return list(self.db.scalars(select(CandidateWallet).offset(offset).limit(limit)).all())

    def get(self, candidate_wallet_id: str) -> CandidateWallet | None:
        return self.db.get(CandidateWallet, candidate_wallet_id)
