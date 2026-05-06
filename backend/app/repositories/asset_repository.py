from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.asset import Asset


class AssetRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, asset_id: str) -> Asset | None:
        return self.db.get(Asset, asset_id)

    def get_by_mint(self, mint_address: str) -> Asset | None:
        return self.db.scalar(select(Asset).where(Asset.mint_address == mint_address))

    def get_or_create_by_mint(
        self,
        mint_address: str,
        symbol: str | None = None,
        name: str | None = None,
        decimals: int | None = None,
        asset_metadata: dict | None = None,
    ) -> Asset:
        asset = self.get_by_mint(mint_address)
        if asset is None:
            asset = Asset(
                mint_address=mint_address,
                symbol=symbol,
                name=name,
                decimals=decimals,
                asset_metadata=asset_metadata or {},
            )
            self.db.add(asset)
            self.db.flush()
            return asset

        if symbol and not asset.symbol:
            asset.symbol = symbol
        if name and not asset.name:
            asset.name = name
        if decimals is not None and asset.decimals is None:
            asset.decimals = decimals
        if asset_metadata:
            asset.asset_metadata = {**asset.asset_metadata, **asset_metadata}
        self.db.flush()
        return asset
