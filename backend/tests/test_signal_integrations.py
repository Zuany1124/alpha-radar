import json
from pathlib import Path

from sqlalchemy.orm import Session

from app.models.wallet import Wallet


def _write_fixture(tmp_path: Path) -> Path:
    fixture_path = tmp_path / "solana_signal_fixture.json"
    fixture_path.write_text(
        json.dumps(
            {
                "wallets": {
                    "SeedWallet1111111111111111111111111111111111": {
                        "history": {
                            "transactions": [
                                {
                                    "signature": "sig-buy-1",
                                    "timestamp": "2026-05-06T00:00:00Z",
                                    "type": "SWAP",
                                    "source": "JUPITER",
                                    "description": "Seed wallet swapped into ALPHA",
                                    "tokenTransfers": [
                                        {
                                            "fromUserAccount": "Pool1111111111111111111111111111111111111",
                                            "toUserAccount": "SeedWallet1111111111111111111111111111111111",
                                            "mint": "MintAlpha111111111111111111111111111111111",
                                            "tokenAmount": 1250,
                                            "symbol": "ALPHA",
                                            "name": "Alpha Token",
                                            "decimals": 6,
                                        }
                                    ],
                                    "nativeTransfers": [],
                                    "events": {},
                                }
                            ],
                            "pagination": {
                                "nextCursor": "cursor-2",
                                "hasMore": False,
                            },
                        },
                        "transfers": {
                            "data": [
                                {
                                    "signature": "transfer-1",
                                    "timestamp": 1778025600,
                                    "direction": "in",
                                    "counterparty": "Counterparty1111111111111111111111111111111",
                                    "mint": "MintAlpha111111111111111111111111111111111",
                                    "amount": 1250,
                                    "symbol": "ALPHA",
                                    "name": "Alpha Token",
                                    "decimals": 6,
                                    "usdValue": 9875.0,
                                }
                            ]
                        },
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    return fixture_path


def test_helius_client_builds_history_and_transfer_requests(monkeypatch) -> None:
    from app.workers.integrations.helius_client import HeliusClient

    observed_requests = []

    class DummyResponse:
        def __init__(self, payload: dict) -> None:
            self.payload = payload

        def read(self) -> bytes:
            return json.dumps(self.payload).encode("utf-8")

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb) -> None:
            return None

    def fake_urlopen(request, timeout: int = 0):
        observed_requests.append(
            {
                "url": request.full_url,
                "headers": dict(request.header_items()),
                "timeout": timeout,
            }
        )
        if "history" in request.full_url:
            return DummyResponse({"transactions": [], "pagination": {"nextCursor": None, "hasMore": False}})
        return DummyResponse({"data": []})

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    client = HeliusClient(api_key="test-key")

    history = client.get_wallet_history("SeedWallet1111111111111111111111111111111111", cursor="abc", limit=25)
    transfers = client.get_wallet_transfers("SeedWallet1111111111111111111111111111111111", limit=15)

    assert history["pagination"]["hasMore"] is False
    assert transfers["data"] == []
    assert observed_requests[0]["url"].endswith(
        "/v1/wallet/SeedWallet1111111111111111111111111111111111/history?limit=25&before=abc&tokenAccounts=balanceChanged"
    )
    assert observed_requests[0]["headers"]["X-api-key"] == "test-key"
    assert observed_requests[1]["url"].endswith(
        "/v1/wallet/SeedWallet1111111111111111111111111111111111/transfers?limit=15"
    )


def test_fixture_provider_normalizes_scores_and_recommends_candidates(tmp_path: Path) -> None:
    from app.models.wallet import Wallet
    from app.workers.integrations.providers import FixtureProvider
    from app.workers.integrations.scoring import score_signal_events
    from app.workers.integrations.tools import normalize_signal_events, recommend_candidate_wallets

    fixture_path = _write_fixture(tmp_path)
    wallet = Wallet(address="SeedWallet1111111111111111111111111111111111", source="manual", status="active")
    provider = FixtureProvider(fixture_path)

    history = provider.fetch_wallet_history(wallet.address)
    transfers = provider.fetch_wallet_transfers(wallet.address)
    events = normalize_signal_events(wallet=wallet, history_page=history, transfers=transfers, scan_id="scan-1")
    scored_events = score_signal_events(events)
    candidates = recommend_candidate_wallets(scored_events, threshold=0.65)

    assert len(scored_events) == 2
    assert max(event.anomaly_score for event in scored_events) >= 0.65
    assert {event.asset_symbol for event in scored_events} == {"ALPHA"}
    assert candidates[0].address == "Counterparty1111111111111111111111111111111"


def test_scan_job_persists_signal_events_and_candidate_wallets(
    db_session: Session,
    monkeypatch,
    tmp_path: Path,
) -> None:
    from app.models.candidate_wallet import CandidateWallet
    from app.models.scan import Scan
    from app.models.signal_event import SignalEvent
    from app.workers.jobs.scan_job import run_scan_job

    fixture_path = _write_fixture(tmp_path)
    wallet = Wallet(address="SeedWallet1111111111111111111111111111111111", source="manual", status="active")
    scan = Scan(trigger="manual", scope={"wallet_ids": []}, status="queued")
    db_session.add_all([wallet, scan])
    db_session.commit()

    monkeypatch.setattr("app.workers.jobs.scan_job.SessionLocal", lambda: db_session)
    monkeypatch.setattr(
        "app.workers.jobs.scan_job.get_settings",
        lambda: type(
            "SettingsStub",
            (),
            {
                "helius_api_key": "",
                "signal_provider": "fixture",
                "signal_fixture_path": str(fixture_path),
                "signal_history_limit": 100,
                "signal_transfers_limit": 100,
                "signal_anomaly_threshold": 0.65,
            },
        )(),
    )

    result = run_scan_job(scan.id)

    signal_events = db_session.query(SignalEvent).all()
    candidates = db_session.query(CandidateWallet).all()

    assert result["status"] == "succeeded"
    assert result["created_signal_event_count"] == 2
    assert result["created_lead_count"] == 1
    assert len(signal_events) == 2
    assert len(candidates) == 1
    assert candidates[0].address == "Counterparty1111111111111111111111111111111"
