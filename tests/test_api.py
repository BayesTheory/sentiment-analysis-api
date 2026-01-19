import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_predict_positive():
    response = client.post("/predict", json={
        "text": "I love this, it's amazing!",
        "lang": "en"
    })
    assert response.status_code == 200
    data = response.json()
    assert "label" in data
    assert "score" in data

def test_predict_empty():
    response = client.post("/predict", json={
        "text": "",
        "lang": "en"
    })
    assert response.status_code == 422  # Validation error

def test_root():
    response = client.get("/")
    assert response.status_code == 200
