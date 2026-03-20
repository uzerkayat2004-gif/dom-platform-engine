"""
Frontend Builder
Auto-generates complete HTML/CSS app frontends.
Every button sends plain English instructions to the DOM server.
No application logic in the frontend — all intelligence is in the DOM model.
"""

import json
from pathlib import Path
from typing import Callable, Optional
from engine.primary_agent.providers import get_provider
from engine.rules.generator import RuleGenerator

class FrontendBuilder:
    
    def __init__(
        self,
        project_id: str,
        provider_name: str,
        api_key: str,
        broadcast_fn: Optional[Callable] = None
    ):
        self.project_id = project_id
        self.provider = get_provider(provider_name, api_key)
        self.rule_gen = RuleGenerator(project_id)
        self.broadcast = broadcast_fn or (lambda x: None)
        self.output_dir = Path(f"projects/{project_id}/frontend")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    async def build(self, domain: str, app_name: str) -> dict:
        """Generate complete frontend for the app."""
        
        await self.broadcast({
            "type": "frontend_building",
            "project_id": self.project_id
        })
        
        skills = self.rule_gen.read("skills_md")
        limits = self.rule_gen.read("limits_md")
        
        prompt = f"""Generate a complete, premium HTML frontend for a {domain} application called "{app_name}".

Skills this app can perform:
{skills}

Limits to display:
{limits}

Requirements:
- Single HTML file with embedded CSS
- Dark theme — background #0a0a1a, surface #0f0f24
- Blue (#3D5AFE) and red (#FF1744) as accent colors
- Premium SaaS quality design — clean, modern, professional
- Every action button sends a fetch POST to http://localhost:5000/process
- Fetch format: fetch('http://localhost:5000/process', {{method:'POST', headers:{{'Content-Type':'application/json'}}, body: JSON.stringify({{instruction: "plain English command here", project_id: "{self.project_id}"}})  }})
- Each button's instruction must be a specific, realistic plain English command
- Include a status/response area that shows the last DOM server response
- Include a current order/state display area that updates after each action
- Include a Glass Box mini-log showing last 5 actions
- No external CSS or JS libraries
- No application logic in JS — only fetch calls and DOM updates
- Responsive layout

Return the complete HTML as a single string. Include ALL CSS in a style tag. No explanations.
"""
        
        html_content = await self.provider.send_message(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=4000,
            temperature=0.3
        )
        
        # Clean up response
        if "```html" in html_content:
            html_content = html_content.split("```html")[1].split("```")[0].strip()
        elif "```" in html_content:
            html_content = html_content.split("```")[1].split("```")[0].strip()
        
        # Save frontend files
        index_path = self.output_dir / "index.html"
        index_path.write_text(html_content)
        
        await self.broadcast({
            "type": "frontend_ready",
            "project_id": self.project_id,
            "path": str(index_path)
        })
        
        return {
            "success": True,
            "path": str(index_path),
            "html": html_content
        }
    
    def get_frontend_path(self) -> Optional[str]:
        """Get path to generated frontend if it exists."""
        index_path = self.output_dir / "index.html"
        if index_path.exists():
            return str(index_path)
        return None
