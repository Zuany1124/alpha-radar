# AlphaRadar Backend Architecture

## 1. Purpose

This document defines the backend architecture for AlphaRadar, a local-first Solana research dashboard that turns wallet activity into traceable research leads.

The backend is not a trading system. It must not store private keys, execute trades, generate order instructions, or expose any automated trading capability. Its responsibility is to collect evidence, structure analysis, and serve auditable research data to the frontend.

## 2. Architecture Goals

- Provide a stable FastAPI resource API for the React dashboard.
- Keep long-running scanning, ingestion, embedding, and agent workflows outside the request lifecycle.
- Preserve traceability from every lead back to chain events, evidence records, and agent runs.
- Support local-first deployment with Docker Compose.
- Keep MVP implementation simple enough to test and replay with fixtures.
- Leave clear boundaries for later production hardening.

## 3. Context7 / FastAPI Notes

Context7 was used to check current FastAPI documentation for the architecture-relevant areas.

Relevant FastAPI guidance:

- `FastAPI.include_router(...)` supports modular `APIRouter` composition with `prefix`, `tags`, `dependencies`, `responses`, `include_in_schema`, and custom OpenAPI behavior.
- Application-wide or router-wide dependencies can be declared with `Depends(...)`.
- Lifespan startup/shutdown logic should use an async context manager passed to `FastAPI(lifespan=...)`.
- `TestClient` should be used with a context manager when tests need lifespan startup/shutdown behavior.
- `app.dependency_overrides` can replace dependencies during tests.
- `BackgroundTasks` is useful for small post-response actions, but AlphaRadar scan and agent workflows should use external workers because they are long-running, failure-prone, and need durable status tracking.

Primary documentation sources returned by Context7:

- https://fastapi.tiangolo.com/reference/fastapi
- https://fastapi.tiangolo.com/advanced/events
- https://fastapi.tiangolo.com/advanced/testing-events
- https://fastapi.tiangolo.com/advanced/testing-dependencies
- https://fastapi.tiangolo.com/tutorial/background-tasks

Context7 was also used to check LangSmith documentation for workflow observability.

Relevant LangSmith guidance:

- LangSmith tracing can be enabled with `LANGSMITH_API_KEY`, `LANGSMITH_TRACING=true`, and `LANGSMITH_PROJECT`.
- LangGraph and supported LLM integrations can automatically emit traces when tracing is enabled.
- Traces can be scoped with project names, tags, metadata, and runtime context.
- LangSmith should be used to debug, monitor, evaluate, and compare LLM workflow behavior over time.

Primary documentation sources returned by Context7:

- https://docs.langchain.com/langsmith/trace-with-langgraph
- https://docs.langchain.com/langsmith/observability-concepts
- https://docs.langchain.com/langsmith/trace-deep-agents
- https://docs.langchain.com/langsmith/log-traces-to-project

## 4. System Boundary

### FastAPI API Service

FastAPI owns the control plane and query plane:

- Wallet and watchlist management.
- Candidate wallet approval or rejection.
- Manual scan trigger.
- Scan status query.
- Lead list and lead detail APIs.
- Evidence and agent run query APIs.
- Health and readiness endpoints.
- OpenAPI documentation for frontend integration.

FastAPI should not perform heavy scanning or agent analysis inline.

### Worker Service

Workers own long-running data and analysis jobs:

- Scheduled wallet scans.
- Manual scan execution.
- Helius API calls.
- Chain event normalization.
- Anomaly scoring.
- Market context collection.
- RAG ingestion and retrieval.
- LangGraph multi-agent workflows.
- LangSmith tracing metadata for workflow observability.
- Lead synthesis.

### Storage and Queue

- Postgres stores durable business records.
- pgvector stores document and evidence embeddings.
- Redis stores queue state, short-lived locks, and job coordination data.
- LangSmith stores external traces, spans, run metadata, debugging context, and evaluation records for LLM workflows.

## 5. High-Level Components

```text
frontend
  |
  v
FastAPI API
  |-- resource routers
  |-- service layer
  |-- repository layer
  |-- OpenAPI docs
  |
  +--> Postgres + pgvector
  |
  +--> Redis queue
          |
          v
       Python workers
          |-- Helius ingestion
          |-- signal scoring
          |-- RAG retrieval
          |-- LangGraph workflow
          |-- OpenAI structured outputs
          |-- LangSmith tracing
```

## 6. Recommended Backend Package Layout

The final implementation can use this structure:

```text
backend/
  app/
    main.py
    api/
      deps.py
      router.py
      v1/
        wallets.py
        candidate_wallets.py
        watchlists.py
        scans.py
        signal_events.py
        leads.py
        evidence.py
        agent_runs.py
    core/
      config.py
      logging.py
      security.py
    db/
      session.py
      base.py
      migrations/
    models/
      wallet.py
      asset.py
      signal_event.py
      evidence_item.py
      lead.py
      agent_run.py
      scan.py
    schemas/
      wallet.py
      scan.py
      lead.py
      evidence.py
      agent_run.py
    services/
      wallet_service.py
      scan_service.py
      lead_service.py
      evidence_service.py
    repositories/
      wallet_repository.py
      scan_repository.py
      lead_repository.py
    workers/
      jobs/
      workflows/
      integrations/
    tests/
  doc/
    architecture.md
```

The exact file split can be refined during implementation, but the direction should stay consistent: routers stay thin, business logic goes into services, persistence details stay behind repositories, and long-running workflows stay in workers.

## 7. FastAPI Application Design

### Router Composition

Use one top-level API router and include resource routers under `/api/v1`.

Recommended resource groups:

- `/api/v1/wallets`
- `/api/v1/candidate-wallets`
- `/api/v1/watchlists`
- `/api/v1/scans`
- `/api/v1/signal-events`
- `/api/v1/leads`
- `/api/v1/evidence`
- `/api/v1/agent-runs`

Each router should define tags so OpenAPI docs remain readable.

### Dependency Injection

Use FastAPI dependencies for request-scoped concerns:

- Database session.
- Current configuration.
- Pagination parameters.
- Optional future authentication context.
- Service construction when useful.

Do not hide heavy business workflows inside dependencies. Dependencies should prepare request context, not run scans or agent workflows.

### Lifespan

Use FastAPI lifespan for startup and shutdown tasks:

- Initialize logging.
- Validate required configuration.
- Check database connectivity.
- Check Redis connectivity.
- Initialize shared lightweight clients if needed.

Do not run migrations, scan jobs, or ingestion jobs from API lifespan. Those should be explicit operational commands or worker responsibilities.

### BackgroundTasks Boundary

FastAPI `BackgroundTasks` may be used for small, best-effort actions after a response, such as lightweight audit logging.

Do not use `BackgroundTasks` for:

- Helius scans.
- RAG ingestion.
- Embedding generation.
- LangGraph workflows.
- Lead synthesis.

Those tasks need queueing, retry policy, status tracking, and failure visibility.

## 8. Core Domain Objects

### Wallet

An approved Solana wallet monitored by the system.

Core fields:

- `id`
- `address`
- `label`
- `notes`
- `source`
- `confidence`
- `status`
- `created_at`
- `updated_at`

### CandidateWallet

A system-recommended wallet that requires user approval before entering the formal watchlist.

Core fields:

- `id`
- `address`
- `recommendation_reason`
- `related_wallet_ids`
- `evidence_ids`
- `status`: `pending`, `approved`, `rejected`
- `reviewed_at`

### Asset

A Solana token or asset referenced by chain events and leads.

Core fields:

- `id`
- `mint_address`
- `symbol`
- `name`
- `decimals`
- `metadata`

### Scan

A scan execution record.

Core fields:

- `id`
- `trigger`: `scheduled` or `manual`
- `scope`
- `status`: `queued`, `running`, `succeeded`, `failed`, `cancelled`
- `started_at`
- `finished_at`
- `error_message`
- `created_signal_event_count`
- `created_lead_count`

### SignalEvent

A normalized chain activity record derived from raw provider data.

Core fields:

- `id`
- `wallet_id`
- `asset_id`
- `event_type`
- `event_timestamp`
- `amount`
- `usd_value`
- `counterparty`
- `raw_provider`
- `raw_payload`
- `anomaly_score`
- `scan_id`

### EvidenceItem

Any evidence used to explain or challenge a lead.

Core fields:

- `id`
- `evidence_type`: `chain`, `market`, `news`, `project_doc`, `agent_note`
- `title`
- `source_url`
- `published_at`
- `fetched_at`
- `summary`
- `metadata`
- `embedding`

### AgentRun

A structured record of an agent or workflow execution.

Core fields:

- `id`
- `workflow_name`
- `agent_name`
- `model`
- `input_payload`
- `output_payload`
- `status`
- `started_at`
- `finished_at`
- `error_message`
- `token_usage`
- `langsmith_project`
- `langsmith_trace_id`
- `langsmith_run_url`
- `trace_tags`
- `trace_metadata`

### Lead

The final research lead shown to the user.

Core fields:

- `id`
- `title`
- `asset_id`
- `primary_wallet_id`
- `signal_summary`
- `why_this_matters`
- `risk_notes`
- `confidence`
- `freshness_timestamp`
- `agent_verdict`
- `related_signal_event_ids`
- `related_evidence_ids`
- `related_agent_run_ids`

## 9. API Resource Design

### Wallets

- `GET /api/v1/wallets`
- `POST /api/v1/wallets`
- `GET /api/v1/wallets/{wallet_id}`
- `PATCH /api/v1/wallets/{wallet_id}`
- `DELETE /api/v1/wallets/{wallet_id}`

### Candidate Wallets

- `GET /api/v1/candidate-wallets`
- `GET /api/v1/candidate-wallets/{candidate_wallet_id}`
- `POST /api/v1/candidate-wallets/{candidate_wallet_id}/approve`
- `POST /api/v1/candidate-wallets/{candidate_wallet_id}/reject`

Approval should create or link a formal `Wallet`. Rejection should be durable so the same candidate is not repeatedly recommended without new evidence.

### Scans

- `GET /api/v1/scans`
- `POST /api/v1/scans`
- `GET /api/v1/scans/{scan_id}`

`POST /api/v1/scans` should enqueue a scan and return quickly with a scan ID and status.

### Leads

- `GET /api/v1/leads`
- `GET /api/v1/leads/{lead_id}`

Lead list should support sorting and filtering by:

- freshness
- confidence
- anomaly score
- asset
- wallet
- verdict

### Evidence

- `GET /api/v1/evidence`
- `GET /api/v1/evidence/{evidence_id}`

Evidence should remain queryable independently from leads so the user can audit source material.

### Agent Runs

- `GET /api/v1/agent-runs`
- `GET /api/v1/agent-runs/{agent_run_id}`

Agent run output should remain structured and replay-friendly.

## 10. Scan and Lead Generation Flow

### Scheduled Scan

1. Scheduler enqueues a scan every 30 minutes.
2. Worker loads approved wallets.
3. Worker calls Helius.
4. Worker normalizes provider data into `SignalEvent`.
5. Scoring service calculates anomaly score.
6. Candidate events above threshold enter analysis workflow.
7. Workflow gathers market context and RAG evidence.
8. LangGraph agents produce structured outputs.
9. Lead synthesizer creates or updates `Lead`.
10. API serves updated leads to the dashboard.

### Manual Scan

1. Frontend calls `POST /api/v1/scans`.
2. API creates a `Scan` record with `queued` status.
3. API enqueues worker job and returns scan ID.
4. Worker updates scan status through lifecycle.
5. Frontend polls scan detail or refreshes lead list.

## 11. Traceability Model

Traceability is a product requirement, not a nice-to-have.

Every lead must preserve references to:

- normalized signal events
- raw provider payloads
- evidence items
- agent runs
- market context
- scan execution

The system should never store only the final natural-language conclusion. The final conclusion is useful only if the user can inspect why it exists and why it may be wrong.

## 12. LangSmith Observability

LangSmith should be the observability layer for LangGraph and LLM workflow execution. Postgres remains the durable application record, while LangSmith provides interactive trace inspection, debugging, monitoring, and evaluation.

### What LangSmith Monitors

LangSmith should capture:

- full LangGraph workflow traces
- per-agent spans
- model inputs and outputs
- tool calls
- retrieval context
- structured output validation failures
- latency
- token usage
- error stack traces
- retry behavior

### Required Trace Metadata

Every workflow trace should include metadata that links LangSmith back to AlphaRadar records:

- `environment`
- `scan_id`
- `lead_id` when available
- `signal_event_ids`
- `wallet_ids`
- `asset_ids`
- `workflow_name`
- `workflow_version`
- `agent_names`
- `model`
- `trigger`: `scheduled` or `manual`

This metadata lets the team move from a lead in the dashboard to the exact LangSmith trace that produced it.

### Project Strategy

Use separate LangSmith projects by environment:

- `alpharadar-local`
- `alpharadar-dev`
- `alpharadar-prod`

Local development can keep tracing optional. Shared development and production-like environments should enable tracing by default for agent workflows.

### Database Relationship

`AgentRun` should store the LangSmith trace identifiers, but LangSmith should not be the only record of execution. The application database still stores:

- workflow input
- structured output
- status
- model name
- error summary
- trace URL or trace ID

This avoids losing auditability if LangSmith is unavailable or if trace retention settings change.

### Evaluation Usage

LangSmith datasets and evaluation should be introduced once fixture-based workflows exist.

Initial evaluation targets:

- lead output follows schema
- risk notes identify weak evidence
- low-liquidity signals are not overconfident
- stale evidence is flagged
- candidate wallet recommendations include explainable evidence

## 13. Testing Strategy

### API Tests

Use FastAPI `TestClient` for endpoint tests.

Required coverage:

- wallet CRUD
- candidate wallet approval/rejection
- manual scan creation
- scan status query
- lead list/detail
- evidence lookup

Tests that rely on app startup/shutdown should use `with TestClient(app) as client`.

### Dependency Overrides

Use `app.dependency_overrides` to replace:

- database session
- queue client
- auth context when introduced
- external service clients

### Worker and Domain Tests

Worker logic should be tested outside FastAPI request tests.

Required coverage:

- Helius fixture normalization
- anomaly score regression fixtures
- noise filtering
- candidate wallet recommendation logic
- lead synthesis schema validation
- RAG retrieval metadata handling

## 14. Configuration

Configuration should be environment-driven.

Expected settings:

- `DATABASE_URL`
- `REDIS_URL`
- `HELIUS_API_KEY`
- `OPENAI_API_KEY`
- `SCAN_INTERVAL_MINUTES`
- `DEFAULT_EMBEDDING_MODEL`
- `DEFAULT_ANALYSIS_MODEL`
- `LANGSMITH_API_KEY`
- `LANGSMITH_TRACING`
- `LANGSMITH_PROJECT`
- `LOG_LEVEL`
- `ENVIRONMENT`

Secrets should not be committed. Local development should use `.env.example` as a template.

## 15. MVP Implementation Phases

### Phase 1: API and Data Foundation

- FastAPI app shell.
- Postgres connection.
- Alembic migrations.
- Core domain tables.
- Wallet CRUD.
- Candidate wallet approval flow.
- Scan record API.

### Phase 2: Scan Data Loop

- Redis queue.
- Worker process.
- Helius integration.
- Signal event normalization.
- Basic anomaly scoring.
- Manual scan trigger.

### Phase 3: Research Lead Loop

- Evidence records.
- RAG ingestion foundation.
- pgvector integration.
- LangGraph workflow skeleton.
- LangSmith tracing for workflow runs.
- Structured lead output.
- Lead list/detail API.

### Phase 4: Quality and Auditability

- Agent run replay records.
- Fixture-based regression tests.
- Noise filtering improvements.
- Lead ranking and filtering.
- Operational health checks.
- LangSmith evaluation datasets for selected fixtures.

## 16. Open Questions

- What is the first seed wallet source and expected wallet count?
- Which market data provider should be used for price, volume, and liquidity?
- Which news/project document sources should be included in MVP RAG ingestion?
- Should MVP remain single-user without authentication?
- Should scan status updates use polling first, or should the API reserve a future websocket/SSE interface?
- What anomaly score threshold should be used for the first fixture-backed implementation?
- Should local LangSmith tracing default to disabled unless explicitly enabled?
- What trace retention policy is acceptable for production-like workflows?

## 17. Architecture Decisions

- Use FastAPI as the API service, not as the worker runtime.
- Use router-level resource modules under `/api/v1`.
- Use dependencies for request context and test overrides.
- Use lifespan for lightweight app startup/shutdown checks.
- Use Redis-backed jobs for scans and agent workflows.
- Use Postgres as the source of truth.
- Use pgvector for embeddings and evidence retrieval.
- Use LangSmith for LangGraph and LLM workflow tracing, monitoring, and evaluation.
- Store LangSmith trace IDs and URLs in `AgentRun` records.
- Keep all lead conclusions traceable and replayable.
