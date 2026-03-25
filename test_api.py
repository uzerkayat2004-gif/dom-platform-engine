import requests
try:
    res = requests.post("http://127.0.0.1:8080/project/create", json={"name": "test", "description": "testing"})
    print("CREATE:", res.status_code, res.text)
except Exception as e:
    print("CREATE ERROR:", e)
    
try:
    res2 = requests.post("http://127.0.0.1:8080/chat", json={
        "project_id": "test",
        "message": "hello",
        "provider": "groq",
        "api_key": "fake_key"
    })
    print("CHAT:", res2.status_code, res2.text)
except Exception as e:
    print("CHAT ERROR:", e)
