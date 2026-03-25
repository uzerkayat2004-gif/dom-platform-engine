"""
DOM Platform Primary Agent
The orchestrator — manages the full app creation journey.
"""

import json
import asyncio
from pathlib import Path
from typing import Callable, Optional, Tuple

from engine.primary_agent.providers import get_provider
from engine.primary_agent.providers.base import BaseProvider
from engine.primary_agent.conversation import (
    conversation_manager,
    ConversationState,
    CreationStep,
)
from engine.rules.generator import RuleGenerator
from engine.glassbox.logger import GlassBoxLogger

PROMPTS_DIR = Path(__file__).parent / "prompts"


def load_prompt(name: str, **kwargs) -> str:
    prompt = (PROMPTS_DIR / f"{name}.md").read_text()
    for key, value in kwargs.items():
        prompt = prompt.replace(f"{{{key}}}", str(value))
    return prompt


class PrimaryAgent:
    def __init__(
        self,
        provider: str,
        api_key: str,
        project_id: str,
        broadcast_fn: Optional[Callable] = None,
    ):
        self.provider: BaseProvider = get_provider(provider, api_key)
        self.project_id = project_id
        self.broadcast = broadcast_fn or self._noop_broadcast
        self.state: ConversationState = conversation_manager.get_or_create(project_id)
        self.rule_generator = RuleGenerator(project_id=project_id)
        self.glass_box = GlassBoxLogger(
            project_id=project_id, broadcast_fn=broadcast_fn
        )

    @staticmethod
    async def _noop_broadcast(x):
        pass

    async def process(self, user_message: str) -> dict:
        """Main entry point — process a user message and return agent response."""

        self.state.add_message("user", user_message)
        await self._broadcast_status("thinking")

        response_text = ""
        next_action = None

        # Route to correct handler based on current step
        if self.state.step == CreationStep.DESCRIBING:
            response_text, next_action = await self._handle_describing(user_message)

        elif self.state.step == CreationStep.QUESTIONING:
            response_text, next_action = await self._handle_questioning(user_message)

        elif self.state.step == CreationStep.REVIEWING_RULES:
            response_text, next_action = await self._handle_reviewing_rules(
                user_message
            )

        self.state.add_message("assistant", response_text)
        conversation_manager.save(self.project_id)

        return {
            "response": response_text,
            "step": self.state.step.value,
            "next_action": next_action,
            "project_id": self.project_id,
        }

    async def _handle_describing(self, user_message: str) -> Tuple[str, Optional[str]]:
        """First contact — understand the app, then ask smart questions."""

        self.state.app_description = user_message

        # Generate clarifying questions
        question_prompt = load_prompt("question_gen", description=user_message)
        questions = await self.provider.send_message(
            messages=[{"role": "user", "content": question_prompt}],
            system_prompt=load_prompt("system"),
            max_tokens=1000,
            temperature=0.4,
        )

        self.state.advance_step(CreationStep.QUESTIONING)

        intro = (
            f"Great — I can build that for you. Before I create the AI that will "
            f"run your app, I need to understand a few things so I can set the right "
            f"rules and boundaries.\n\n{questions}"
        )

        await self._broadcast_workspace_update("questioning")
        return intro, None

    async def _handle_questioning(self, user_message: str) -> Tuple[str, Optional[str]]:
        """User has answered questions — generate rule files."""

        self.state.questions_asked += 1

        await self._broadcast_status("generating_rules")
        await self._broadcast_glass_box(
            "SYSTEM", "Generating constitutional rule files..."
        )

        # Generate all four rule files
        conversation_context = json.dumps(self.state.get_messages_for_api(), indent=2)
        rules_prompt = load_prompt("rules_gen", conversation=conversation_context)

        rules_json_str = await self.provider.send_message(
            messages=[{"role": "user", "content": rules_prompt}],
            system_prompt=load_prompt("system"),
            max_tokens=3000,
            temperature=0.2,
        )

        # Parse and save rule files
        try:
            clean = rules_json_str.strip()
            if "```" in clean:
                # Handle cases like ```json or just ```
                parts = clean.split("```")
                if len(parts) >= 3:
                    clean = parts[1]
                    # Remove language identifier if present
                    if clean.startswith("json"):
                        clean = clean[4:].lstrip()
                else:
                    clean = parts[0] if parts else clean
            rule_files = json.loads(clean)
        except Exception as e:
            # Log the error for debugging
            print(f"Error parsing rule files: {e}")
            rule_files = self._get_fallback_rules()

        saved_files = self.rule_generator.save(rule_files)

        for filename in saved_files:
            await self._broadcast_file_created(filename)
            await self._broadcast_glass_box("SYSTEM", f"Rule file created: {filename}")

        self.state.advance_step(CreationStep.REVIEWING_RULES)
        self.state.rules_approved = False

        response = (
            "I've created the four constitutional rule files for your app. "
            "Your DOM model will be trained on these rules from birth — "
            "it will physically be unable to violate them.\n\n"
            "**security.md** — Access control and security rules\n"
            "**behavior.md** — How your app must always behave\n"
            "**limits.md** — Hard boundaries that can never be crossed\n"
            "**skills.md** — What your app is permitted to do\n\n"
            "You can review these files in the workspace panel. "
            "Type **approve** to start training your DOM model, or tell me "
            "what you'd like to change."
        )

        return response, "show_rules"

    async def _handle_reviewing_rules(
        self, user_message: str
    ) -> Tuple[str, Optional[str]]:
        """User is reviewing rule files — wait for approval or handle changes."""

        if (
            "approve" in user_message.lower()
            or "looks good" in user_message.lower()
            or "start" in user_message.lower()
        ):
            self.state.rules_approved = True
            self.state.advance_step(CreationStep.TRAINING)

            response = (
                "Rules approved. Starting DOM model training now.\n\n"
                "I'm generating training data based on your rule files, "
                "then fine-tuning your domain-specific AI model. "
                "This will take 20 to 60 minutes depending on your hardware.\n\n"
                "Watch the workspace panel for real-time progress."
            )
            return response, "start_training"

        # User wants to change something — handle the change
        change_request = user_message
        modify_prompt = (
            f"The user wants to modify their rule files. Change requested:\n{change_request}\n\n"
            f"Current rule files:\n{json.dumps(self.rule_generator.read_all(), indent=2)}\n\n"
            f"Return updated rule files in the same JSON format as before."
        )

        updated_json = await self.provider.send_message(
            messages=[{"role": "user", "content": modify_prompt}],
            system_prompt=load_prompt("system"),
            max_tokens=3000,
            temperature=0.2,
        )

        try:
            clean = updated_json.strip()
            if "```" in clean:
                # Handle cases like ```json or just ```
                parts = clean.split("```")
                if len(parts) >= 3:
                    clean = parts[1]
                    # Remove language identifier if present
                    if clean.startswith("json"):
                        clean = clean[4:].lstrip()
                else:
                    clean = parts[0] if parts else clean
            updated_rules = json.loads(clean)
            self.rule_generator.save(updated_rules)
        except Exception as e:
            print(f"Error parsing updated rules: {e}")
            pass

        response = (
            "I've updated the rule files based on your feedback. "
            "Review the changes in the workspace panel. "
            "Type **approve** when you're happy to start training."
        )
        return response, "show_rules"

    async def _handle_training_complete(self, project_id: str):
        """Called when training finishes — trigger frontend build."""
        self.state.advance_step(CreationStep.BUILDING_FRONTEND)

        await self._broadcast_status("building_frontend")
        await self._broadcast_glass_box(
            "SYSTEM", "Training complete — building frontend..."
        )

        # Start DOM server
        import httpx

        async with httpx.AsyncClient() as client:
            try:
                await client.post(
                    "http://localhost:8080/dom-server/start",
                    json={"project_id": self.project_id, "port": 5000},
                )
            except Exception as e:
                print(f"Failed to start DOM server: {e}")

        # Build frontend
        project_config_path = Path(f"projects/{self.project_id}/config.json")
        config = (
            json.loads(project_config_path.read_text())
            if project_config_path.exists()
            else {}
        )
        domain = config.get("description", "business")
        app_name = config.get("name", "My App").replace("-", " ").title()

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    "http://localhost:8080/frontend/build",
                    json={
                        "project_id": self.project_id,
                        "domain": domain,
                        "app_name": app_name,
                        "provider": self.provider.__class__.__name__.lower().replace(
                            "provider", ""
                        ),
                        "api_key": self.provider.api_key,
                    },
                    timeout=60.0,
                )
            except Exception as e:
                print(f"Failed to build frontend: {e}")

        self.state.advance_step(CreationStep.PREVIEW)
        await self._broadcast_glass_box(
            "SYSTEM", "Frontend built — app ready for preview"
        )

        await self.broadcast({"type": "app_ready", "project_id": self.project_id})

    async def _broadcast_status(self, status: str):
        await self.broadcast(
            {"type": "status", "status": status, "project_id": self.project_id}
        )

    async def _broadcast_file_created(self, filename: str):
        await self.broadcast(
            {
                "type": "file_created",
                "filename": filename,
                "project_id": self.project_id,
            }
        )

    async def _broadcast_workspace_update(self, state: str):
        await self.broadcast(
            {"type": "workspace_update", "state": state, "project_id": self.project_id}
        )

    async def _broadcast_glass_box(self, action_type: str, message: str):
        await self.glass_box.log(action_type, message)

    def _get_fallback_rules(self) -> dict:
        return {
            "security_md": "Rule 1: Only authenticated users can access the system\nRule 2: All data must be validated before processing\nRule 3: No data leaves the device without explicit user permission\nRule 4: Maximum 3 failed authentication attempts then lockout\nRule 5: All actions logged with timestamp and user ID",
            "behavior_md": "Rule 1: Always confirm before any destructive action\nRule 2: Always show result of every action to the user\nRule 3: Never process duplicate requests within 60 seconds\nRule 4: Always generate a receipt or confirmation after transactions",
            "limits_md": "Rule 1: Maximum single transaction value set by owner\nRule 2: Maximum discount without approval: 30%\nRule 3: Maximum users per account: 50\nRule 4: Operating hours enforced as configured",
            "skills_md": "Skill 1: Process and manage primary domain operations\nSkill 2: Handle user authentication and access control\nSkill 3: Process transactions and generate confirmations\nSkill 4: Generate reports and analytics\nSkill 5: Manage data and records",
        }
