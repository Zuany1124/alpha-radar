from fastapi import APIRouter

from app.api.v1 import agent_runs, candidate_wallets, evidence, leads, scans, wallets

api_router = APIRouter()
api_router.include_router(wallets.router, prefix="/wallets", tags=["wallets"])
api_router.include_router(candidate_wallets.router, prefix="/candidate-wallets", tags=["candidate-wallets"])
api_router.include_router(scans.router, prefix="/scans", tags=["scans"])
api_router.include_router(leads.router, prefix="/leads", tags=["leads"])
api_router.include_router(evidence.router, prefix="/evidence", tags=["evidence"])
api_router.include_router(agent_runs.router, prefix="/agent-runs", tags=["agent-runs"])
