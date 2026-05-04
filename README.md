# Solana Alpha Evidence Radar

Solana Alpha Evidence Radar is a local-first research dashboard for monitoring Solana smart-wallet activity and turning noisy on-chain movement into traceable research leads.

The project focuses on evidence collection, risk review, and structured analysis. It does not execute trades, store private keys, or generate automated order instructions.

## Current Contents

- `docs/solana-alpha-evidence-radar-requirements.md` - product requirements and MVP scope.
- `docs/DESIGN.md` - visual design direction and interface system notes.

## Planned Stack

- React dashboard.
- FastAPI resource API.
- Python workers for scheduled scanning and analysis.
- Postgres with pgvector for structured records and evidence embeddings.
- Redis-backed queue for asynchronous jobs.
- LangGraph multi-agent analysis workflow.
- Docker Compose for local-first deployment.

