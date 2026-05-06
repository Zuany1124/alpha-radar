from sqlalchemy.orm import Session

from app.models.candidate_wallet import CandidateWallet


def test_candidate_wallet_approval_creates_wallet(client, db_session: Session) -> None:
    candidate = CandidateWallet(
        address="Cand111111111111111111111111111111111111111",
        recommendation_reason="Repeated co-movement with a seed wallet",
        related_wallet_ids=[],
        evidence_ids=[],
    )
    db_session.add(candidate)
    db_session.commit()

    response = client.post(f"/api/v1/candidate-wallets/{candidate.id}/approve")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "approved"
    assert body["wallet"]["address"] == "Cand111111111111111111111111111111111111111"

    candidate_response = client.get(f"/api/v1/candidate-wallets/{candidate.id}")
    assert candidate_response.status_code == 200
    assert candidate_response.json()["status"] == "approved"


def test_candidate_wallet_rejection_is_durable(client, db_session: Session) -> None:
    candidate = CandidateWallet(
        address="Reject111111111111111111111111111111111111",
        recommendation_reason="Weak related evidence",
        related_wallet_ids=[],
        evidence_ids=[],
    )
    db_session.add(candidate)
    db_session.commit()

    response = client.post(f"/api/v1/candidate-wallets/{candidate.id}/reject")

    assert response.status_code == 200
    assert response.json()["status"] == "rejected"

    repeat_response = client.post(f"/api/v1/candidate-wallets/{candidate.id}/approve")
    assert repeat_response.status_code == 409
