"""创建核心数据表

Revision ID: 0001_create_core_tables
Revises:
Create Date: 2026-05-05
"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "0001_create_core_tables"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "wallets",
        sa.Column("address", sa.String(length=128), nullable=False),
        sa.Column("label", sa.String(length=160), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("source", sa.String(length=80), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_wallets_address"), "wallets", ["address"], unique=True)

    op.create_table(
        "candidate_wallets",
        sa.Column("address", sa.String(length=128), nullable=False),
        sa.Column("recommendation_reason", sa.Text(), nullable=False),
        sa.Column("related_wallet_ids", sa.JSON(), nullable=False),
        sa.Column("evidence_ids", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_candidate_wallets_address"), "candidate_wallets", ["address"], unique=True)

    op.create_table(
        "scans",
        sa.Column("trigger", sa.String(length=32), nullable=False),
        sa.Column("scope", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_signal_event_count", sa.Integer(), nullable=False),
        sa.Column("created_lead_count", sa.Integer(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "assets",
        sa.Column("mint_address", sa.String(length=128), nullable=False),
        sa.Column("symbol", sa.String(length=32), nullable=True),
        sa.Column("name", sa.String(length=160), nullable=True),
        sa.Column("decimals", sa.Integer(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_assets_mint_address"), "assets", ["mint_address"], unique=True)

    op.create_table(
        "evidence_items",
        sa.Column("evidence_type", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=240), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.Column("embedding", sa.JSON(), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "agent_runs",
        sa.Column("workflow_name", sa.String(length=120), nullable=False),
        sa.Column("agent_name", sa.String(length=120), nullable=True),
        sa.Column("model", sa.String(length=120), nullable=True),
        sa.Column("input_payload", sa.JSON(), nullable=False),
        sa.Column("output_payload", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("token_usage", sa.JSON(), nullable=False),
        sa.Column("langsmith_project", sa.String(length=160), nullable=True),
        sa.Column("langsmith_trace_id", sa.String(length=160), nullable=True),
        sa.Column("langsmith_run_url", sa.Text(), nullable=True),
        sa.Column("trace_tags", sa.JSON(), nullable=False),
        sa.Column("trace_metadata", sa.JSON(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "signal_events",
        sa.Column("wallet_id", sa.String(length=36), nullable=True),
        sa.Column("asset_id", sa.String(length=36), nullable=True),
        sa.Column("event_type", sa.String(length=80), nullable=False),
        sa.Column("event_timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("amount", sa.Numeric(precision=36, scale=12), nullable=True),
        sa.Column("usd_value", sa.Numeric(precision=36, scale=6), nullable=True),
        sa.Column("counterparty", sa.String(length=128), nullable=True),
        sa.Column("raw_provider", sa.String(length=64), nullable=True),
        sa.Column("raw_payload", sa.JSON(), nullable=False),
        sa.Column("anomaly_score", sa.Float(), nullable=True),
        sa.Column("scan_id", sa.String(length=36), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"]),
        sa.ForeignKeyConstraint(["scan_id"], ["scans.id"]),
        sa.ForeignKeyConstraint(["wallet_id"], ["wallets.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "leads",
        sa.Column("title", sa.String(length=240), nullable=False),
        sa.Column("asset_id", sa.String(length=36), nullable=True),
        sa.Column("primary_wallet_id", sa.String(length=36), nullable=True),
        sa.Column("signal_summary", sa.Text(), nullable=False),
        sa.Column("why_this_matters", sa.Text(), nullable=True),
        sa.Column("risk_notes", sa.Text(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("freshness_timestamp", sa.DateTime(timezone=True), nullable=True),
        sa.Column("agent_verdict", sa.String(length=80), nullable=True),
        sa.Column("related_signal_event_ids", sa.JSON(), nullable=False),
        sa.Column("related_evidence_ids", sa.JSON(), nullable=False),
        sa.Column("related_agent_run_ids", sa.JSON(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"]),
        sa.ForeignKeyConstraint(["primary_wallet_id"], ["wallets.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("leads")
    op.drop_table("signal_events")
    op.drop_table("agent_runs")
    op.drop_table("evidence_items")
    op.drop_index(op.f("ix_assets_mint_address"), table_name="assets")
    op.drop_table("assets")
    op.drop_table("scans")
    op.drop_index(op.f("ix_candidate_wallets_address"), table_name="candidate_wallets")
    op.drop_table("candidate_wallets")
    op.drop_index(op.f("ix_wallets_address"), table_name="wallets")
    op.drop_table("wallets")
