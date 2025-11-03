from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from ..main import app

client = TestClient(app)


def test_create_transaction():
    data = {
        "description": "Test Transaction",
        "transaction_date": datetime.utcnow().isoformat(),
        "reference": "REF123",
        "entries": [
            {
                "account_id": 1,
                "amount": 100.0,
                "entry_type": "debit",
                "description": "Test entry",
            },
            {
                "account_id": 2,
                "amount": 100.0,
                "entry_type": "credit",
                "description": "Test entry",
            },
        ],
    }
    response = client.post("/transactions/transactions/", json=data)
    assert response.status_code == 200
    result = response.json()
    assert result["description"] == "Test Transaction"
    assert len(result["entries"]) == 2


def test_get_transaction():
    # Create a transaction first
    data = {
        "description": "Get Transaction",
        "transaction_date": datetime.utcnow().isoformat(),
        "reference": "REF456",
        "entries": [
            {
                "account_id": 1,
                "amount": 50.0,
                "entry_type": "debit",
                "description": "Entry 1",
            },
            {
                "account_id": 2,
                "amount": 50.0,
                "entry_type": "credit",
                "description": "Entry 2",
            },
        ],
    }
    create_resp = client.post("/transactions/transactions/", json=data)
    assert create_resp.status_code == 200
    tx_id = create_resp.json()["id"]
    # Now get it
    get_resp = client.get(f"/transactions/transactions/{tx_id}")
    assert get_resp.status_code == 200
    tx = get_resp.json()
    assert tx["id"] == tx_id
    assert tx["description"] == "Get Transaction"


def test_update_transaction():
    # Create a transaction first
    data = {
        "description": "Update Transaction",
        "transaction_date": datetime.utcnow().isoformat(),
        "reference": "REF789",
        "entries": [
            {
                "account_id": 1,
                "amount": 20.0,
                "entry_type": "debit",
                "description": "Entry 1",
            },
            {
                "account_id": 2,
                "amount": 20.0,
                "entry_type": "credit",
                "description": "Entry 2",
            },
        ],
    }
    create_resp = client.post("/transactions/transactions/", json=data)
    assert create_resp.status_code == 200
    tx_id = create_resp.json()["id"]
    # Update
    update_data = {
        "description": "Updated Transaction",
        "transaction_date": datetime.utcnow().isoformat(),
        "reference": "REF999",
        "entries": [
            {
                "account_id": 1,
                "amount": 10.0,
                "entry_type": "debit",
                "description": "Entry 1",
            },
            {
                "account_id": 2,
                "amount": 10.0,
                "entry_type": "credit",
                "description": "Entry 2",
            },
        ],
    }
    update_resp = client.put(f"/transactions/transactions/{tx_id}", json=update_data)
    assert update_resp.status_code == 200
    tx = update_resp.json()
    assert tx["description"] == "Updated Transaction"
    assert len(tx["entries"]) == 2


def test_delete_transaction():
    # Create a transaction first
    data = {
        "description": "Delete Transaction",
        "transaction_date": datetime.utcnow().isoformat(),
        "reference": "REFDEL",
        "entries": [
            {
                "account_id": 1,
                "amount": 5.0,
                "entry_type": "debit",
                "description": "Entry 1",
            },
            {
                "account_id": 2,
                "amount": 5.0,
                "entry_type": "credit",
                "description": "Entry 2",
            },
        ],
    }
    create_resp = client.post("/transactions/transactions/", json=data)
    assert create_resp.status_code == 200
    tx_id = create_resp.json()["id"]
    # Delete
    del_resp = client.delete(f"/transactions/transactions/{tx_id}")
    assert del_resp.status_code == 200
    assert del_resp.json()["detail"] == "Transaction deleted"
    assert del_resp.status_code == 200
    assert del_resp.json()["detail"] == "Transaction deleted"
