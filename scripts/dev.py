"""
DOM Platform Dev Starter
Starts the complete platform — Engine + Tauri UI
Run: python scripts/dev.py
"""

import subprocess
import sys
import time
import threading
from pathlib import Path

def start_engine():
    print("=" * 50)
    print("DOM PLATFORM ENGINE — Starting on localhost:8080")
    print("=" * 50)
    
    project_root = Path(__file__).parent.parent
    
    # Auto-detect virtual environment
    venv_python = project_root / ".venv" / "Scripts" / "python.exe"
    if not venv_python.exists():
        venv_python = project_root / ".venv" / "bin" / "python"
        
    python_exe = str(venv_python) if venv_python.exists() else sys.executable
    
    subprocess.run([
        python_exe, "-m", "uvicorn",
        "engine.main:app",
        "--host", "127.0.0.1",
        "--port", "8080",
        "--reload"
    ], cwd=str(project_root))

def start_tauri():
    time.sleep(4)
    print("=" * 50)
    print("DOM PLATFORM UI — Starting Tauri desktop app")
    print("=" * 50)
    
    import os
    shell = os.name == 'nt'
    subprocess.run(["npm", "run", "tauri", "dev"], shell=shell, cwd=str(Path(__file__).parent.parent))

if __name__ == "__main__":
    print()
    print("╔══════════════════════════════════════════════╗")
    print("║       DOM PLATFORM — CATEGORY C ENGINE       ║")
    print("║         Starting all services...             ║")
    print("╚══════════════════════════════════════════════╝")
    print()
    
    engine_thread = threading.Thread(target=start_engine, daemon=True)
    engine_thread.start()
    
    try:
        start_tauri()
    except KeyboardInterrupt:
        sys.exit(0)
