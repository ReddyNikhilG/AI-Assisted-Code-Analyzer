from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "ast_parsing" in data["features"]

def test_analyze_endpoint():
    code = """
import os
password = "admin"
query = "SELECT * FROM users WHERE id = " + user_input
"""
    response = client.post("/analyze", json={"code": code})
    assert response.status_code == 200
    data = response.json()
    
    # Assert features parsed
    assert len(data["imports"]) == 1
    assert len(data["variables"]) == 2
    
    # Assert risks detected
    assert len(data["risks"]) > 0
    risk_types = [risk["type"] for risk in data["risks"]]
    assert "SQL Injection" in risk_types
    assert "Hardcoded Credential" in risk_types

def test_cache_hits():
    code = "import sys\nprint(sys.argv)"
    
    response1 = client.post("/analyze", json={"code": code})
    assert response1.status_code == 200
    data1 = response1.json()
    
    response2 = client.post("/analyze", json={"code": code})
    assert response2.status_code == 200
    data2 = response2.json()
    
    assert data1 == data2
