from fastapi.testclient import TestClient

from src.order_service.main import app


client = TestClient(app)


def test_create_order_endpoint_returns_pending():
    response = client.post("/orders", json={"product_ids": ["prod1"], "amount": 45.0})
    assert response.status_code == 201
    payload = response.json()
    assert payload["status"] == "PENDING"
    assert payload["product_ids"] == ["prod1"]
    assert "id" in payload


def test_trigger_event_updates_order_state():
    create_response = client.post("/orders", json={"product_ids": ["prod1"], "amount": 80.0})
    order_id = create_response.json()["id"]

    event_response = client.post(f"/orders/{order_id}/events", json={"event_type": "noVerificationNeeded", "metadata": {}})
    assert event_response.status_code == 200
    assert event_response.json()["status"] == "PENDING_PAYMENT"

    get_response = client.get(f"/orders/{order_id}")
    assert get_response.status_code == 200
    assert len(get_response.json()["history"]) == 1


def test_trigger_event_returns_404_for_unknown_order():
    response = client.post("/orders/non-existing-id/events", json={"event_type": "noVerificationNeeded", "metadata": {}})
    assert response.status_code == 404


def test_trigger_event_returns_422_for_invalid_transition():
    create_response = client.post("/orders", json={"product_ids": ["prod1"], "amount": 35.0})
    order_id = create_response.json()["id"]

    response = client.post(f"/orders/{order_id}/events", json={"event_type": "itemDispatched", "metadata": {}})
    assert response.status_code == 422
