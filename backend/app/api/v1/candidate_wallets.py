from fastapi import APIRouter, Depends

from app.api.deps import get_candidate_wallet_service
from app.schemas.candidate_wallet import CandidateWalletApproval, CandidateWalletList, CandidateWalletRead
from app.services.candidate_wallet_service import CandidateWalletService

router = APIRouter()


@router.get("", response_model=CandidateWalletList)
def list_candidate_wallets(
    limit: int = 50,
    offset: int = 0,
    service: CandidateWalletService = Depends(get_candidate_wallet_service),
) -> CandidateWalletList:
    """查询 CandidateWallet 列表。"""

    return CandidateWalletList(items=service.list_candidates(limit=limit, offset=offset))


@router.get("/{candidate_wallet_id}", response_model=CandidateWalletRead)
def get_candidate_wallet(
    candidate_wallet_id: str,
    service: CandidateWalletService = Depends(get_candidate_wallet_service),
):
    """查询 CandidateWallet 详情。"""

    return service.get_candidate(candidate_wallet_id)


@router.post("/{candidate_wallet_id}/approve", response_model=CandidateWalletApproval)
def approve_candidate_wallet(
    candidate_wallet_id: str,
    service: CandidateWalletService = Depends(get_candidate_wallet_service),
) -> CandidateWalletApproval:
    """批准 CandidateWallet 并创建 Wallet。"""

    candidate, wallet = service.approve(candidate_wallet_id)
    return CandidateWalletApproval(status=candidate.status, wallet=wallet)


@router.post("/{candidate_wallet_id}/reject", response_model=CandidateWalletRead)
def reject_candidate_wallet(
    candidate_wallet_id: str,
    service: CandidateWalletService = Depends(get_candidate_wallet_service),
):
    """拒绝 CandidateWallet。"""

    return service.reject(candidate_wallet_id)
