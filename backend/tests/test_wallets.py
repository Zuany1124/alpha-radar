from fastapi.testclient import TestClient


def test_wallet_crud(client: TestClient) -> None:
    create_response = client.post(
        "/api/v1/wallets",
        json={
            "address": "9xQeWvG816bUx9EPfWfBa7DPTbQsvqKkdZ2wLQf9Y5J",
            "label": "Seed wallet",
            "notes": "Known smart wallet",
            "source": "manual",
            "confidence": 0.8,
        },
    )
    assert create_response.status_code == 201
    wallet = create_response.json()
    assert wallet["address"] == "9xQeWvG816bUx9EPfWfBa7DPTbQsvqKkdZ2wLQf9Y5J"
    assert wallet["status"] == "active"

    wallet_id = wallet["id"]
    detail_response = client.get(f"/api/v1/wallets/{wallet_id}")
    assert detail_response.status_code == 200
    assert detail_response.json()["label"] == "Seed wallet"

    list_response = client.get("/api/v1/wallets")
    assert list_response.status_code == 200
    assert [item["id"] for item in list_response.json()["items"]] == [wallet_id]

    patch_response = client.patch(f"/api/v1/wallets/{wallet_id}", json={"label": "Updated seed"})
    assert patch_response.status_code == 200
    assert patch_response.json()["label"] == "Updated seed"

    delete_response = client.delete(f"/api/v1/wallets/{wallet_id}")
    assert delete_response.status_code == 204

    missing_response = client.get(f"/api/v1/wallets/{wallet_id}")
    assert missing_response.status_code == 404
