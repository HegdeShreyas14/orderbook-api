from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_order():
    response = client.post(
        "/orders" ,
        json={
            "side":"buy",
            "type":"limit",
            "price":100,
            "qty":10
        })

    assert response.status_code == 201

    data = response.json()

    assert data["side"] == "buy"
    assert data["price"] == 100
    assert data["qty"] == 10
    assert data["fill_qty"] == 0
    assert data["status"] == "open"
