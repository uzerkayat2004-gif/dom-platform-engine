import requests
if __name__ == "__main__":
    try:
        res2 = requests.post("http://127.0.0.1:8081/chat", json={
            "project_id": "test",
            "message": "hello",
            "provider": "groq",
            "api_key": "fake_key"
        })
        print("CHAT:", res2.status_code, res2.text)
    except Exception as e:
        print("CHAT ERROR:", e)
