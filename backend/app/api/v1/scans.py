from fastapi import APIRouter, Depends, status

from app.api.deps import get_scan_service
from app.schemas.scan import ScanCreate, ScanList, ScanRead
from app.services.scan_service import ScanService

router = APIRouter()


@router.get("", response_model=ScanList)
def list_scans(
    limit: int = 50,
    offset: int = 0,
    service: ScanService = Depends(get_scan_service),
) -> ScanList:
    """查询 Scan 列表。"""

    return ScanList(items=service.list_scans(limit=limit, offset=offset))


@router.post("", response_model=ScanRead, status_code=status.HTTP_201_CREATED)
def create_scan(payload: ScanCreate, service: ScanService = Depends(get_scan_service)):
    """创建手动 Scan 并写入队列。"""

    return service.create_scan(payload)


@router.get("/{scan_id}", response_model=ScanRead)
def get_scan(scan_id: str, service: ScanService = Depends(get_scan_service)):
    """查询 Scan 详情。"""

    return service.get_scan(scan_id)
