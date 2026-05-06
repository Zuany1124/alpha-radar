from fastapi import APIRouter, Depends

from app.api.deps import get_evidence_service
from app.schemas.evidence import EvidenceList, EvidenceRead
from app.services.evidence_service import EvidenceService

router = APIRouter()


@router.get("", response_model=EvidenceList)
def list_evidence(
    limit: int = 50,
    offset: int = 0,
    evidence_type: str | None = None,
    service: EvidenceService = Depends(get_evidence_service),
) -> EvidenceList:
    """查询 EvidenceItem 列表。"""

    return EvidenceList(
        items=service.list_evidence(limit=limit, offset=offset, evidence_type=evidence_type)
    )


@router.get("/{evidence_id}", response_model=EvidenceRead)
def get_evidence(
    evidence_id: str,
    service: EvidenceService = Depends(get_evidence_service),
):
    """查询 EvidenceItem 详情。"""

    return service.get_evidence(evidence_id)
