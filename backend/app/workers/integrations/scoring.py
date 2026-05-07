from __future__ import annotations

from app.workers.integrations.tools import NormalizedSignalEvent


def score_signal_events(events: list[NormalizedSignalEvent]) -> list[NormalizedSignalEvent]:
    for event in events:
        score = 0.15
        usd_value = float(event.usd_value or 0)
        amount = float(event.amount or 0)

        if usd_value >= 10000:
            score += 0.45
        elif usd_value >= 5000:
            score += 0.35
        elif usd_value >= 1000:
            score += 0.2
        elif amount >= 1000:
            score += 0.1

        if event.event_type in {"swap_in", "transfer_in"}:
            score += 0.15
        else:
            score += 0.05

        if event.counterparty:
            score += 0.1
        if event.asset_mint:
            score += 0.05
        if event.asset_symbol:
            score += 0.05

        event.anomaly_score = round(min(score, 0.99), 2)

    return events
