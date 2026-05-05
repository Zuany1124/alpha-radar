from fastapi import APIRouter, Depends, Query

from app.api.deps import get_lead_service
from app.schemas.lead import LeadDetailRead, LeadList
from app.services.lead_service import LeadService

router = APIRouter()


@router.get("", response_model=LeadList)
def list_leads(
    limit: int = 50,
    offset: int = 0,
    asset_id: str | None = None,
    primary_wallet_id: str | None = None,
    agent_verdict: str | None = None,
    min_confidence: float | None = Query(default=None, ge=0, le=1),
    service: LeadService = Depends(get_lead_service),
) -> LeadList:
    """查询 Lead 列表。"""

    return LeadList(
        items=service.list_leads(
            limit=limit,
            offset=offset,
            asset_id=asset_id,
            primary_wallet_id=primary_wallet_id,
            agent_verdict=agent_verdict,
            min_confidence=min_confidence,
        )
    )


@router.get("/{lead_id}", response_model=LeadDetailRead)
def get_lead(lead_id: str, service: LeadService = Depends(get_lead_service)) -> LeadDetailRead:
    """查询 Lead 详情。"""

    return service.get_lead_detail(lead_id)
