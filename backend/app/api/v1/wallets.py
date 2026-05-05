from fastapi import APIRouter, Depends, Response, status

from app.schemas.wallet import WalletCreate, WalletList, WalletRead, WalletUpdate
from app.services.wallet_service import WalletService
from app.api.deps import get_wallet_service

router = APIRouter()


@router.get("", response_model=WalletList)
def list_wallets(
    limit: int = 50,
    offset: int = 0,
    service: WalletService = Depends(get_wallet_service),
) -> WalletList:
    """查询 Wallet 列表。"""

    return WalletList(items=service.list_wallets(limit=limit, offset=offset))


@router.post("", response_model=WalletRead, status_code=status.HTTP_201_CREATED)
def create_wallet(
    payload: WalletCreate,
    service: WalletService = Depends(get_wallet_service),
):
    """创建 Wallet。"""

    return service.create_wallet(payload)


@router.get("/{wallet_id}", response_model=WalletRead)
def get_wallet(wallet_id: str, service: WalletService = Depends(get_wallet_service)):
    """查询 Wallet 详情。"""

    return service.get_wallet(wallet_id)


@router.patch("/{wallet_id}", response_model=WalletRead)
def update_wallet(
    wallet_id: str,
    payload: WalletUpdate,
    service: WalletService = Depends(get_wallet_service),
):
    """更新 Wallet。"""

    return service.update_wallet(wallet_id, payload)


@router.delete("/{wallet_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_wallet(wallet_id: str, service: WalletService = Depends(get_wallet_service)) -> Response:
    """删除 Wallet。"""

    service.delete_wallet(wallet_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
