from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.wallet import Wallet
from app.schemas.wallet import WalletCreate, WalletUpdate


class WalletRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self, limit: int = 50, offset: int = 0) -> list[Wallet]:
        return list(self.db.scalars(select(Wallet).offset(offset).limit(limit)).all())

    def list_active(self, wallet_ids: list[str] | None = None) -> list[Wallet]:
        stmt = select(Wallet).where(Wallet.status == "active").order_by(Wallet.created_at.asc())
        if wallet_ids:
            stmt = stmt.where(Wallet.id.in_(wallet_ids))
        return list(self.db.scalars(stmt).all())

    def get(self, wallet_id: str) -> Wallet | None:
        return self.db.get(Wallet, wallet_id)

    def get_by_address(self, address: str) -> Wallet | None:
        return self.db.scalar(select(Wallet).where(Wallet.address == address))

    def create(self, payload: WalletCreate) -> Wallet:
        wallet = Wallet(**payload.model_dump())
        self.db.add(wallet)
        self.db.commit()
        self.db.refresh(wallet)
        return wallet

    def create_from_candidate(self, address: str, source: str, notes: str | None = None) -> Wallet:
        existing = self.get_by_address(address)
        if existing:
            return existing
        wallet = Wallet(address=address, source=source, notes=notes, status="active")
        self.db.add(wallet)
        self.db.flush()
        return wallet

    def update(self, wallet: Wallet, payload: WalletUpdate) -> Wallet:
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(wallet, field, value)
        self.db.commit()
        self.db.refresh(wallet)
        return wallet

    def delete(self, wallet: Wallet) -> None:
        self.db.delete(wallet)
        self.db.commit()
