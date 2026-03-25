import pytest
from engine.dom_server.server import dom_app

@pytest.fixture
def client():
    """A test client for the app."""
    dom_app.config['TESTING'] = True
    with dom_app.test_client() as client:
        yield client

def test_health_check(client):
    """Test the health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    assert response.get_json() == {"status": "running", "server": "DOM Server"}

def test_process_missing_instruction(client):
    """Test that POST /process without instruction returns 400 Bad Request"""
    response = client.post('/process', json={"project_id": "test_proj"})
    assert response.status_code == 400
    assert response.get_json() == {"error": "No instruction provided"}

def test_process_empty_instruction(client):
    """Test that POST /process with empty instruction returns 400 Bad Request"""
    response = client.post('/process', json={"instruction": "", "project_id": "test_proj"})
    assert response.status_code == 400
    assert response.get_json() == {"error": "No instruction provided"}
