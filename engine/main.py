"""
DOM Platform Engine — Main Server
FastAPI server at localhost:8080
Handles all communication between the Tauri UI and the Python engine.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import asyncio
import json
import shutil
import threading
from pathlib import Path
from datetime import datetime
# dom_server imported lazily inside /dom-server/start endpoint

app = FastAPI(title="DOM Platform Engine", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connections for real-time updates to the UI
active_connections: list[WebSocket] = []

async def broadcast(message: dict):
    """Send real-time updates to all connected UI clients."""
    for connection in active_connections:
        try:
            await connection.send_json(message)
        except:
            pass

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections.remove(websocket)

class ChatMessage(BaseModel):
    project_id: str
    message: str
    provider: str = "groq"
    api_key: str = ""

class ProjectCreate(BaseModel):
    name: str
    description: str

class ApiKeyTest(BaseModel):
    provider: str
    api_key: str

@app.get("/health")
async def health():
    return {"status": "running", "version": "0.1.0", "provider": "Engine Ready"}

@app.post("/chat")
async def chat(data: ChatMessage):
    """Main chat endpoint — receives user message, returns agent response."""
    from engine.primary_agent.agent import PrimaryAgent
    agent = PrimaryAgent(
        provider=data.provider,
        api_key=data.api_key,
        project_id=data.project_id,
        broadcast_fn=broadcast
    )
    try:
        response = await agent.process(data.message)
        return response
    except Exception as e:
        err = str(e)
        # Friendly messages for common errors
        if "invalid_api_key" in err or "AuthenticationError" in err or "401" in err:
            friendly = f"Authentication failed. Your {data.provider} API key looks invalid. Please go to Settings and update it."
        elif "rate_limit" in err or "429" in err:
            friendly = "Rate limit hit. Please wait a moment before sending another message."
        elif "Connection" in err or "connect" in err.lower():
            friendly = "Network error reaching the AI provider. Check your internet connection."
        else:
            friendly = f"Engine error: {err[:200]}"
        return {
            "response": friendly,
            "step": "describing",
            "next_action": None,
            "project_id": data.project_id
        }

def validate_path(path: Path):
    """Ensure the path is within the projects directory."""
    base_dir = Path("projects").resolve()
    # Resolve the path to handle traversal like ../
    try:
        resolved_path = path.resolve()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid path")

    # Check if the resolved path is within the base directory
    try:
        resolved_path.relative_to(base_dir)
    except ValueError:
        raise HTTPException(status_code=400, detail="Path traversal detected")
    return resolved_path

@app.post("/project/create")
async def create_project(data: ProjectCreate):
    """Create a new project folder structure."""
    project_path = Path(f"projects/{data.name}")
    validate_path(project_path)
    project_path.mkdir(parents=True, exist_ok=True)
    (project_path / "rules").mkdir(exist_ok=True)
    (project_path / "training").mkdir(exist_ok=True)
    (project_path / "model").mkdir(exist_ok=True)
    (project_path / "frontend").mkdir(exist_ok=True)
    (project_path / "glassbox").mkdir(exist_ok=True)
    config = {
        "name": data.name,
        "description": data.description,
        "status": "created",
        "step": "describing",
        "created_at": datetime.now().isoformat()
    }
    (project_path / "config.json").write_text(json.dumps(config, indent=2))
    return {"success": True, "project_id": data.name, "path": str(project_path)}

@app.get("/projects")
async def list_projects():
    """List all projects."""
    projects_dir = Path("projects")
    projects = []
    if projects_dir.exists():
        for p in projects_dir.iterdir():
            if p.is_dir():
                config_file = p / "config.json"
                if config_file.exists():
                    projects.append(json.loads(config_file.read_text()))
    return {"projects": projects}

@app.get("/conversation/{project_id}")
async def get_conversation(project_id: str):
    """Return saved conversation history for a project."""
    convo_path = Path(f"projects/{project_id}/conversation.json")
    validate_path(convo_path)
    if not convo_path.exists():
        return {"messages": [], "step": "describing"}
    data = json.loads(convo_path.read_text())
    return {
        "messages": data.get("messages", []),
        "step": data.get("step", "describing")
    }

@app.post("/projects/clear")
async def clear_projects():
    """Delete all projects for development cleanup."""
    projects_dir = Path("projects")
    if projects_dir.exists():
        shutil.rmtree(projects_dir)
    projects_dir.mkdir()
    return {"cleared": True}

@app.get("/project/{project_id}")
async def get_project(project_id: str):
    """Get project status and config."""
    config_path = Path(f"projects/{project_id}/config.json")
    validate_path(config_path)
    if not config_path.exists():
        return {"error": "Project not found"}
    return json.loads(config_path.read_text())

@app.post("/api-key/test")
async def test_api_key(data: ApiKeyTest):
    """Test if an API key is valid."""
    from engine.primary_agent.providers import get_provider
    try:
        provider = get_provider(data.provider, data.api_key)
        result = await provider.test_connection()
        return {"valid": result, "provider": data.provider}
    except Exception as e:
        return {"valid": False, "error": str(e)}

@app.get("/rule-file/{project_id}/{filename}")
async def get_rule_file(project_id: str, filename: str):
    """Get the content of a specific rule file."""
    file_path = Path(f"projects/{project_id}/rules/{filename}")
    validate_path(file_path)
    if not file_path.exists():
        return {"content": None, "exists": False}
    return {"content": file_path.read_text(), "exists": True}

@app.get("/project-files/{project_id}")
async def get_project_files(project_id: str):
    """List all files in a project directory."""
    project_path = Path(f"projects/{project_id}")
    validate_path(project_path)
    if not project_path.exists():
        return {"files": []}
    files = []
    rules_dir = project_path / "rules"
    if rules_dir.exists():
        for f in rules_dir.iterdir():
            if f.is_file():
                files.append({"name": f.name, "path": str(f), "size": f.stat().st_size})
    return {"files": files, "project_id": project_id}

class TrainRequest(BaseModel):
    provider: str = "groq"
    api_key: str = ""

@app.post("/train/{project_id}")
async def start_training(project_id: str, data: TrainRequest):
    """Start DOM model training for a project."""
    asyncio.create_task(run_training(project_id, data.provider, data.api_key))
    return {"status": "started", "project_id": project_id}

async def run_training(project_id: str, provider: str, api_key: str):
    from engine.training.data_generator import TrainingDataGenerator
    from engine.training.fine_tuner import FineTuner
    
    # 1. Generate Dataset using Primary (Groq) and Secondary (Nova)
    await broadcast({"type": "training_progress", "message": "Phase 1: Generating training data...", "project_id": project_id})
    generator = TrainingDataGenerator(
        project_id=project_id,
        provider_name=provider,
        api_key=api_key,
        broadcast_fn=broadcast
    )
    await generator.generate(count=15)
    
    # 2. Fine-Tune the small model
    await broadcast({"type": "training_progress", "message": "Phase 2: Fine-Tuning the model...", "project_id": project_id})
    tuner = FineTuner(project_id=project_id, broadcast_fn=broadcast)
    await tuner.run()

class StartDOMServer(BaseModel):
    project_id: str
    port: int = 5000

@app.post("/dom-server/start")
async def start_dom(data: StartDOMServer):
    """Start the DOM server for a project in a background thread."""
    from engine.dom_server.server import start_dom_server
    thread = threading.Thread(
        target=start_dom_server,
        args=(data.project_id, data.port),
        daemon=True
    )
    thread.start()
    return {"status": "started", "port": data.port, "project_id": data.project_id}

class BuildFrontend(BaseModel):
    project_id: str
    domain: str
    app_name: str
    provider: str = "groq"
    api_key: str = ""

@app.post("/frontend/build")
async def build_frontend(data: BuildFrontend):
    """Generate the app frontend."""
    from engine.frontend_builder.builder import FrontendBuilder
    builder = FrontendBuilder(
        project_id=data.project_id,
        provider_name=data.provider,
        api_key=data.api_key,
        broadcast_fn=broadcast
    )
    result = await builder.build(data.domain, data.app_name)
    return result

@app.get("/frontend/{project_id}")
async def get_frontend(project_id: str):
    """Get the generated frontend HTML."""
    frontend_path = Path(f"projects/{project_id}/frontend/index.html")
    validate_path(frontend_path)
    if not frontend_path.exists():
        return {"error": "Frontend not built yet"}
    return {"html": frontend_path.read_text(), "path": str(frontend_path)}

class DeployProject(BaseModel):
    project_id: str

@app.post("/deploy")
async def deploy_project(data: DeployProject):
    """Deploy the project (placeholder endpoint for MVP)."""
    return {"status": "success", "url": f"https://{data.project_id}.dom.app"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080, log_level="info")
