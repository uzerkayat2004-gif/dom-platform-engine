import asyncio
import json
import logging
import requests
import websockets
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(message)s")

API_BASE = "http://127.0.0.1:8080"
WS_URL = "ws://127.0.0.1:8080/ws"

async def test_flow():
    print("=== DOM Platform Engine Test ===")
    
    # 1. Health check (user req 2)
    try:
        r = requests.get(f"{API_BASE}/health")
        print(f"\n[Health Check] GET /health -> {r.json()}")
    except Exception as e:
        print(f"[Health Check] Failed: {e}")
        return

    # 2. Create Project
    print("\n[Creating Project]")
    payload = {
        "name": "Indian POS Test",
        "description": "I want to build a restaurant POS system for an Indian restaurant"
    }
    r = requests.post(f"{API_BASE}/project/create", json=payload)
    proj_data = r.json()
    project_id = proj_data.get("project_id")
    print(f"Created project: {project_id}")

    # 3. Connect WebSocket (simulate UI)
    print("\n[Connecting WebSocket]")
    try:
        ws = await websockets.connect(WS_URL)
        print("WebSocket connected.")
    except Exception as e:
        print(f"WebSocket failed: {e}")
        return

    # 4. Start listening task
    async def listen():
        try:
            while True:
                msg = await asyncio.wait_for(ws.recv(), timeout=2.0)
                data = json.loads(msg)
                if data.get("project_id") != project_id: continue
                
                dtype = data.get("type")
                if dtype == "status":
                    print(f"  [UI Status] {data['status']}")
                elif dtype == "glass_box_entry":
                    entry = data["entry"]
                    print(f"  [Glass Box] {entry['type_label']} - {entry['message']}")
                elif dtype == "file_created":
                    print(f"  [Workspace] File appeared: {data['filename']}")
        except asyncio.TimeoutError:
            pass # just checking
        except Exception as e:
            pass

    listen_task = asyncio.create_task(listen())

    # 5. Send initial chat message (User Req 3)
    print(f"\n[Sending Chat]: {payload['description']}")
    
    # Async request to chat
    def send_chat():
        return requests.post(f"{API_BASE}/chat", json={
            "project_id": project_id,
            "message": payload['description'],
            "provider": "groq",
            "api_key": "" # default for mock/test if any, wait, we didn't specify a key.
                          # The groq client will fail if no key and no env var.
                          # I will use a dummy provider if possible, but Groq needs a key.
                          # Wait, I don't have an API key. Let me see what happens.
        })
    
    # We await the chat response
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, send_chat)
    
    print("\n[Agent Response] (User Req 4):")
    try:
        chat_res = response.json()
        print(chat_res.get("response", "No response text"))
    except Exception as e:
        print("Failed to decode chat response:", response.text)
    
    listen_task.cancel()

if __name__ == "__main__":
    asyncio.run(test_flow())
