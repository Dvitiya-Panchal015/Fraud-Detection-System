import pytest
from fastapi.testclient import TestClient

from backend.app.main import app


TRANSACTION = {
    "step": 1,
    "amount": 9839.64,
    "transaction_type": "PAYMENT",
    "old_balance_origin": 170136.0,
    "new_balance_origin": 160296.36,
    "old_balance_destination": 0.0,
    "new_balance_destination": 0.0,
}


def test_prediction_returns_probability_and_threshold() -> None:
    with TestClient(app) as client:
        response = client.post("/api/v1/predict", json=TRANSACTION)

    assert response.status_code == 200
    result = response.json()
    assert set(result) == {
        "prediction",
        "fraud_probability",
        "threshold",
        "message",
    }
    assert 0 <= result["fraud_probability"] <= 1
    assert result["threshold"] == pytest.approx(0.9)
    assert result["prediction"] == int(
        result["fraud_probability"] >= result["threshold"]
    )


@pytest.mark.parametrize(
    "changes",
    [
        {"amount": -1},
        {"transaction_type": "WIRE"},
        {"isFraud": 0},
        {"amount": float("nan")},
    ],
)
def test_invalid_transaction_returns_422(changes: dict[str, object]) -> None:
    transaction = {**TRANSACTION, **changes}

    with TestClient(app) as client:
        response = client.post("/api/v1/predict", json=transaction)

    assert response.status_code == 422