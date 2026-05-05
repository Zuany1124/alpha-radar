from fastapi import HTTPException, status

from app.models.evidence_item import EvidenceItem
from app.repositories.evidence_repository import EvidenceRepository


class EvidenceService:
    """EvidenceItem 只读资源服务。"""

    def __init__(self, evidence: EvidenceRepository) -> None:
        self.evidence = evidence

    def list_evidence(
        self,
        limit: int,
        offset: int,
        evidence_type: str | None = None,
    ) -> list[EvidenceItem]:
        """分页查询证据资源。"""

        return self.evidence.list(limit=limit, offset=offset, evidence_type=evidence_type)

    def get_evidence(self, evidence_id: str) -> EvidenceItem:
        """查询单条证据，不存在时返回 404。"""

        evidence = self.evidence.get(evidence_id)
        if evidence is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evidence not found")
        return evidence
