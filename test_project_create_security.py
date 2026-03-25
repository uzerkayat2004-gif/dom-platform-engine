import pytest
from fastapi.testclient import TestClient
from engine.main import app

client = TestClient(app)

def test_create_project_security_traversal():
    """Test that path traversal characters in project names are rejected."""
    payload = {
        "name": "../invalid_project",
        "description": "This should fail"
    }
    response = client.post("/project/create", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid project name"

def test_create_project_security_absolute_path():
    """Test that absolute paths in project names are rejected."""
    payload = {
        "name": "/tmp/root_project",
        "description": "This should fail"
    }
    response = client.post("/project/create", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid project name"

def test_create_project_security_valid():
    """Test that valid project names are accepted."""
    payload = {
        "name": "valid-project_name 123",
        "description": "This should succeed"
    }
    response = client.post("/project/create", json=payload)
    assert response.status_code == 200
    assert response.json()["success"] == True
    assert response.json()["project_id"] == "valid-project_name 123"
