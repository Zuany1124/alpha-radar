from __future__ import annotations

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

    def get_by_address(self, address: str) -> CandidateWallet | None:
        return self.db.scalar(select(CandidateWallet).where(CandidateWallet.address == address))

    def upsert_pending(
        self,
        address: str,
        recommendation_reason: str,
        related_wallet_ids: list[str],
        evidence_ids: list[str],
    ) -> CandidateWallet:
        candidate = self.get_by_address(address)
        if candidate is None:
            candidate = CandidateWallet(
                address=address,
                recommendation_reason=recommendation_reason,
                related_wallet_ids=related_wallet_ids,
                evidence_ids=evidence_ids,
                status="pending",
            )
            self.db.add(candidate)
            self.db.flush()
            return candidate

        if candidate.status == "rejected":
            return candidate

        candidate.recommendation_reason = recommendation_reason
        candidate.related_wallet_ids = related_wallet_ids
        candidate.evidence_ids = evidence_ids
        if candidate.status != "approved":
            candidate.status = "pending"
        self.db.flush()
        return candidate
