import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_create_account():
    response = client.post("/accounts/", json={"name": "Test Account", "balance": 100.0})
    assert response.status_code == 201
    assert response.json()["name"] == "Test Account"

def test_get_account():
    response = client.get("/accounts/1")
    assert response.status_code == 200
    assert "name" in response.json()

def test_update_account():
    response = client.put("/accounts/1", json={"name": "Updated Account", "balance": 150.0})
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Account"

def test_delete_account():
    response = client.delete("/accounts/1")
    assert response.status_code == 204