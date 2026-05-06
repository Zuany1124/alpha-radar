from collections.abc import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.db.session import get_session
from app.repositories.candidate_wallet_repository import CandidateWalletRepository
from app.repositories.agent_run_repository import AgentRunRepository
from app.repositories.evidence_repository import EvidenceRepository
from app.repositories.lead_repository import LeadRepository
from app.repositories.scan_repository import ScanRepository
from app.repositories.wallet_repository import WalletRepository
from app.services.agent_run_service import AgentRunService
from app.services.candidate_wallet_service import CandidateWalletService
from app.services.evidence_service import EvidenceService
from app.services.lead_service import LeadService
from app.services.scan_service import ScanService
from app.services.wallet_service import WalletService
from app.workers.queue import QueueClient, RedisQueueClient


def get_db() -> Generator[Session, None, None]:
    """提供请求级数据库会话。"""

    yield from get_session()


def get_queue_client(settings: Settings = Depends(get_settings)) -> QueueClient:
    """创建队列客户端。"""

    return RedisQueueClient(settings.redis_url)


def get_wallet_service(db: Session = Depends(get_db)) -> WalletService:
    """创建 Wallet 服务。"""

    return WalletService(WalletRepository(db))


def get_candidate_wallet_service(db: Session = Depends(get_db)) -> CandidateWalletService:
    """创建 CandidateWallet 服务。"""

    return CandidateWalletService(CandidateWalletRepository(db), WalletRepository(db))


def get_scan_service(
    db: Session = Depends(get_db),
    queue: QueueClient = Depends(get_queue_client),
) -> ScanService:
    """创建 Scan 服务。"""

    return ScanService(ScanRepository(db), queue)


def get_lead_service(db: Session = Depends(get_db)) -> LeadService:
    """创建 Lead 查询服务。"""

    return LeadService(LeadRepository(db), EvidenceRepository(db), AgentRunRepository(db))


def get_evidence_service(db: Session = Depends(get_db)) -> EvidenceService:
    """创建 EvidenceItem 查询服务。"""

    return EvidenceService(EvidenceRepository(db))


def get_agent_run_service(db: Session = Depends(get_db)) -> AgentRunService:
    """创建 AgentRun 查询服务。"""

    return AgentRunService(AgentRunRepository(db))
