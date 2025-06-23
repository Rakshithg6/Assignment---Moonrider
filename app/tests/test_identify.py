import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db, SessionLocal
from app.models import Contact

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_contacts_table():
    # Ensure a clean DB state before each test
    init_db()
    db = SessionLocal()
    db.query(Contact).delete()
    db.commit()
    db.close()
    yield


def test_create_primary():
    resp = client.post("/identify", json={"email": "doc@z.com", "phoneNumber": "123"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["primaryContactId"] > 0
    assert data["emails"] == ["doc@z.com"]
    assert data["phoneNumbers"] == ["123"]
    assert data["secondaryContactIds"] == []


def test_link_secondary():
    # First create
    client.post("/identify", json={"email": "doc@z.com", "phoneNumber": "123"})
    # New info, same email, new phone
    resp = client.post("/identify", json={"email": "doc@z.com", "phoneNumber": "456"})
    assert resp.status_code == 200
    data = resp.json()
    assert set(data["emails"]) == {"doc@z.com"}
    assert set(data["phoneNumbers"]) == {"123", "456"}
    assert len(data["secondaryContactIds"]) == 1


def test_merge_contacts():
    # Create two primaries
    client.post("/identify", json={"email": "a@z.com", "phoneNumber": "111"})
    client.post("/identify", json={"email": "b@z.com", "phoneNumber": "222"})
    # Overlap
    resp = client.post("/identify", json={"email": "a@z.com", "phoneNumber": "222"})
    data = resp.json()
    assert set(data["emails"]) == {"a@z.com", "b@z.com"}
    assert set(data["phoneNumbers"]) == {"111", "222"}
    assert len(data["secondaryContactIds"]) >= 1
