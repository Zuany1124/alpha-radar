from datetime import timezone

from fastapi import HTTPException, status

from app.models.candidate_wallet import CandidateWallet
from app.models.mixins import now_utc
from app.models.wallet import Wallet
from app.repositories.candidate_wallet_repository import CandidateWalletRepository
from app.repositories.wallet_repository import WalletRepository


class CandidateWalletService:
    def __init__(self, candidates: CandidateWalletRepository, wallets: WalletRepository) -> None:
        self.candidates = candidates
        self.wallets = wallets

    def list_candidates(self, limit: int, offset: int) -> list[CandidateWallet]:
        return self.candidates.list(limit=limit, offset=offset)

    def get_candidate(self, candidate_wallet_id: str) -> CandidateWallet:
        candidate = self.candidates.get(candidate_wallet_id)
        if candidate is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate wallet not found")
        return candidate

    def approve(self, candidate_wallet_id: str) -> tuple[CandidateWallet, Wallet]:
        candidate = self.get_candidate(candidate_wallet_id)
        if candidate.status != "pending":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Candidate already reviewed")

        wallet = self.wallets.create_from_candidate(
            address=candidate.address,
            source="candidate_approval",
            notes=candidate.recommendation_reason,
        )
        candidate.status = "approved"
        candidate.reviewed_at = now_utc()
        self.candidates.db.commit()
        self.candidates.db.refresh(candidate)
        self.candidates.db.refresh(wallet)
        return candidate, wallet

    def reject(self, candidate_wallet_id: str) -> CandidateWallet:
        candidate = self.get_candidate(candidate_wallet_id)
        if candidate.status != "pending":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Candidate already reviewed")

        candidate.status = "rejected"
        candidate.reviewed_at = now_utc()
        self.candidates.db.commit()
        self.candidates.db.refresh(candidate)
        return candidate
