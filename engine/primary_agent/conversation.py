"""
Conversation state manager.
Tracks the full conversation history and the current step
in the app creation journey for each project.
"""

import json
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Optional
from enum import Enum

class CreationStep(str, Enum):
    DESCRIBING = "describing"
    QUESTIONING = "questioning"
    REVIEWING_RULES = "reviewing_rules"
    TRAINING = "training"
    BUILDING_FRONTEND = "building_frontend"
    PREVIEW = "preview"
    DEPLOYED = "deployed"

@dataclass
class Message:
    role: str          # "user" or "assistant"
    content: str
    step: CreationStep = CreationStep.DESCRIBING

@dataclass
class ConversationState:
    project_id: str
    step: CreationStep = CreationStep.DESCRIBING
    messages: List[Message] = field(default_factory=list)
    app_description: str = ""
    questions_asked: int = 0
    rules_approved: bool = False
    
    def add_message(self, role: str, content: str):
        self.messages.append(Message(role=role, content=content, step=self.step))
    
    def get_messages_for_api(self) -> List[dict]:
        return [{"role": m.role, "content": m.content} for m in self.messages]
    
    def advance_step(self, next_step: CreationStep):
        self.step = next_step
    
    def to_dict(self) -> dict:
        return {
            "project_id": self.project_id,
            "step": self.step.value,
            "messages": [asdict(m) for m in self.messages],
            "app_description": self.app_description,
            "questions_asked": self.questions_asked,
            "rules_approved": self.rules_approved
        }

class ConversationManager:
    """Manages conversation state for all active projects."""
    
    def __init__(self):
        self._states: dict[str, ConversationState] = {}
    
    def get_or_create(self, project_id: str) -> ConversationState:
        if project_id not in self._states:
            self._states[project_id] = ConversationState(project_id=project_id)
            self._load_from_disk(project_id)
        return self._states[project_id]
    
    def save(self, project_id: str):
        state = self._states.get(project_id)
        if not state:
            return
        save_path = Path(f"projects/{project_id}/conversation.json")
        save_path.parent.mkdir(parents=True, exist_ok=True)
        save_path.write_text(json.dumps(state.to_dict(), indent=2))
    
    def _load_from_disk(self, project_id: str):
        load_path = Path(f"projects/{project_id}/conversation.json")
        if not load_path.exists():
            return
        data = json.loads(load_path.read_text())
        state = self._states[project_id]
        state.step = CreationStep(data.get("step", "describing"))
        state.app_description = data.get("app_description", "")
        state.questions_asked = data.get("questions_asked", 0)
        state.rules_approved = data.get("rules_approved", False)
        for m in data.get("messages", []):
            state.messages.append(Message(
                role=m["role"],
                content=m["content"],
                step=CreationStep(m.get("step", "describing"))
            ))

conversation_manager = ConversationManager()
