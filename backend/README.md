# AlphaRadar Backend

FastAPI API service and Python worker scaffold for AlphaRadar.

## Commands

```bash
uv sync
uv run uvicorn app.main:app --reload
uv run pytest
uv run alembic upgrade head
```

The API is the control/query plane. Long-running scan and lead analysis work belongs in workers under `app/workers`.
