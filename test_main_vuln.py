from fastapi.testclient import TestClient
from engine.main import app

client = TestClient(app)

def run_tests():
    # Valid ID
    res = client.get("/project-files/test_project")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    print("Normal test passed.")

    # Invalid characters (Path traversal payloads)
    traversal_payloads = [
        "..%5C..%5Cetc%5Cpasswd",  # URL-encoded backslashes
        "../../../etc/passwd",      # Regular forward slashes
        "..%2F..%2Fetc%2Fpasswd",   # URL-encoded forward slashes
        "test@project",             # Invalid char @
        "project id",               # Space
        "projects/test_project",    # Slash
    ]

    for payload in traversal_payloads:
        res = client.get(f"/project-files/{payload}")
        assert res.status_code in [400, 404], f"Expected 400 or 404 for payload '{payload}', got {res.status_code}. Response: {res.text}"
        if res.status_code == 400:
            assert "Invalid project_id format" in res.text, f"Unexpected error message: {res.text}"
            print(f"Payload '{payload}' caught by regex validation (400 Bad Request).")
        else:
            print(f"Payload '{payload}' caught by FastAPI routing (404 Not Found).")

    print("All security tests passed.")

if __name__ == "__main__":
    run_tests()
