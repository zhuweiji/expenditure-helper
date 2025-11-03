import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_create_entry():
    response = client.post("/entries/", json={"account_id": 1, "amount": 100.0})
    assert response.status_code == 201
    assert response.json()["amount"] == 100.0

def test_read_entry():
    response = client.get("/entries/1/")
    assert response.status_code == 200
    assert "amount" in response.json()

def test_update_entry():
    response = client.put("/entries/1/", json={"amount": 150.0})
    assert response.status_code == 200
    assert response.json()["amount"] == 150.0

def test_delete_entry():
    response = client.delete("/entries/1/")
    assert response.status_code == 204