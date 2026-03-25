import pytest
from fastapi.testclient import TestClient
from engine.main import app
import os

client = TestClient(app)

def test_path_traversal_prevention_get_project():
    """Test that directory traversal in get_project is blocked with 400 Bad Request."""
    # FastApi testclient handles %2F as a literal slash in path sometimes, or routing resolves it.
    # To test exactly the path parameter containing a slash or dot-dot, we can pass it directly.
    response = client.get("/project/foo%5Cbar")
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid path segment"

def test_rule_file():
    response = client.get("/rule-file/valid_project/..%5Cfilename")
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid path segment"

import shutil

@pytest.fixture
def create_test_project():
    """Fixture to create and clean up a test project."""
    os.makedirs("projects/valid_project/rules", exist_ok=True)
    with open("projects/valid_project/config.json", "w") as f:
        f.write('{"name": "valid_project"}')
    yield
    # Cleanup after test
    if os.path.exists("projects/valid_project"):
        shutil.rmtree("projects/valid_project")

def test_valid_project_id_works(create_test_project):
    """Ensure valid project IDs are not blocked."""
    response = client.get("/project/valid_project")
    assert response.status_code == 200
    assert response.json()["name"] == "valid_project"

    response = client.get("/rule-file/valid_project/missing.txt")
    assert response.status_code == 200
    assert response.json()["exists"] == False
