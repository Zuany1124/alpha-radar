from fastapi import HTTPException, status

from app.models.lead import Lead
from app.repositories.agent_run_repository import AgentRunRepository
from app.repositories.evidence_repository import EvidenceRepository
from app.repositories.lead_repository import LeadRepository
from app.schemas.lead import LeadDetailRead


class LeadService:
    """Lead 查询和详情展开服务。"""

    def __init__(
        self,
        leads: LeadRepository,
        evidence: EvidenceRepository,
        agent_runs: AgentRunRepository,
    ) -> None:
        self.leads = leads
        self.evidence = evidence
        self.agent_runs = agent_runs

    def list_leads(
        self,
        limit: int,
        offset: int,
        asset_id: str | None = None,
        primary_wallet_id: str | None = None,
        agent_verdict: str | None = None,
        min_confidence: float | None = None,
    ) -> list[Lead]:
        """分页查询 Lead 资源。"""

        return self.leads.list(
            limit=limit,
            offset=offset,
            asset_id=asset_id,
            primary_wallet_id=primary_wallet_id,
            agent_verdict=agent_verdict,
            min_confidence=min_confidence,
        )

    def get_lead(self, lead_id: str) -> Lead:
        """查询单条 Lead，不存在时返回 404。"""

        lead = self.leads.get(lead_id)
        if lead is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
        return lead

    def get_lead_detail(self, lead_id: str) -> LeadDetailRead:
        """查询 Lead 详情，并展开关联证据和 AgentRun。"""

        lead = self.get_lead(lead_id)
        evidence_items = self.evidence.get_many(lead.related_evidence_ids)
        agent_runs = self.agent_runs.get_many(lead.related_agent_run_ids)
        return LeadDetailRead.model_validate(lead).model_copy(
            update={"evidence_items": evidence_items, "agent_runs": agent_runs}
        )
