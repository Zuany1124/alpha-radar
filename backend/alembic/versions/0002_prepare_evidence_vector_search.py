"""准备 evidence 向量检索扩展

Revision ID: 0002_prepare_evidence_vector_search
Revises: 0001_create_core_tables
Create Date: 2026-05-07
"""
from collections.abc import Sequence

from alembic import op

revision: str = "0002_prepare_evidence_vector_search"
down_revision: str | None = "0001_create_core_tables"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("CREATE EXTENSION IF NOT EXISTS vector")


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("DROP EXTENSION IF EXISTS vector")
