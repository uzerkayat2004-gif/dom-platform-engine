"""
Glass Box Logger
Real-time activity logger for the DOM model.
Every action, every rule check, every security decision — logged in plain English.
"""

import datetime
from pathlib import Path
from typing import Callable, Optional

class GlassBoxLogger:
    
    ACTION_TYPES = {
        "SECURITY_BLOCK": "🔴 BLOCKED",
        "RULE_CHECK": "✅ PASSED",
        "ASSEMBLY": "⚙️  ASSEMBLY",
        "ORDER": "📋 ORDER",
        "PAYMENT": "💰 PAYMENT",
        "KITCHEN": "🍳 KITCHEN",
        "SYSTEM": "🔧 SYSTEM",
        "INFO": "ℹ️  INFO"
    }
    
    def __init__(self, project_id: str, broadcast_fn: Optional[Callable] = None):
        self.project_id = project_id
        self.broadcast = broadcast_fn or self._noop
        self.log_file = Path(f"projects/{project_id}/glassbox/activity.log")
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    async def _noop(x):
        pass
    
    async def log(self, action_type: str, message: str, rule_check: str = ""):
        """Log an action and broadcast it to the UI."""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        type_label = self.ACTION_TYPES.get(action_type, "ℹ️  INFO")
        
        entry = f"[{timestamp}] {type_label}  {message}"
        if rule_check:
            entry += f" — {rule_check}"
        
        # Write to log file
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(entry + "\n")
        
        # Broadcast to UI in real time
        await self.broadcast({
            "type": "glass_box_entry",
            "entry": {
                "timestamp": timestamp,
                "action_type": action_type,
                "type_label": type_label,
                "message": message,
                "rule_check": rule_check,
                "full_entry": entry,
                "is_blocked": action_type == "SECURITY_BLOCK"
            },
            "project_id": self.project_id
        })
    
    def get_recent(self, lines: int = 50) -> list:
        """Get the most recent log entries."""
        if not self.log_file.exists():
            return []
        all_lines = self.log_file.read_text(encoding="utf-8").strip().split("\n")
        return all_lines[-lines:]
