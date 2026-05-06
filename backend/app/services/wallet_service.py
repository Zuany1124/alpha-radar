from fastapi import HTTPException, status

from app.models.wallet import Wallet
from app.repositories.wallet_repository import WalletRepository
from app.schemas.wallet import WalletCreate, WalletUpdate


class WalletService:
    def __init__(self, wallets: WalletRepository) -> None:
        self.wallets = wallets

    def list_wallets(self, limit: int, offset: int) -> list[Wallet]:
        return self.wallets.list(limit=limit, offset=offset)

    def get_wallet(self, wallet_id: str) -> Wallet:
        wallet = self.wallets.get(wallet_id)
        if wallet is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found")
        return wallet

    def create_wallet(self, payload: WalletCreate) -> Wallet:
        if self.wallets.get_by_address(payload.address):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Wallet already exists")
        return self.wallets.create(payload)

    def update_wallet(self, wallet_id: str, payload: WalletUpdate) -> Wallet:
        return self.wallets.update(self.get_wallet(wallet_id), payload)

    def delete_wallet(self, wallet_id: str) -> None:
        self.wallets.delete(self.get_wallet(wallet_id))
