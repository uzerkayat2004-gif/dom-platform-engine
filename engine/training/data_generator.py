"""
Training Data Generator
Uses the Primary Agent to generate instruction-response JSONL pairs
constrained by the project's rule files.
"""

import json
import aiofiles
from pathlib import Path
from typing import Callable, Optional, List
from engine.primary_agent.providers import get_provider
from engine.rules.generator import RuleGenerator

class TrainingDataGenerator:
    
    def __init__(
        self,
        project_id: str,
        provider_name: str,
        api_key: str,
        broadcast_fn: Optional[Callable] = None
    ):
        self.project_id = project_id
        self.provider = get_provider(provider_name, api_key)
        self.rule_generator = RuleGenerator(project_id)
        self.broadcast = broadcast_fn or self._noop
        self.output_path = Path(f"projects/{project_id}/training/dataset.jsonl")
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    async def _noop(x):
        pass
    
    async def generate(self, count: int = 100) -> List[dict]:
        """Generate count training examples and save to JSONL."""
        
        rule_files = self.rule_generator.get_combined_rules()
        
        prompt = f"""Generate {count} training examples for a DOM model.

Rule files:
{rule_files}

Return a JSON array. Each item must have exactly:
- instruction: realistic plain English command
- assembly: x86 assembly (mov, add, sub, etc.) that executes this
- rule_check: "PASSED" or "BLOCKED: [reason]"
- result: what happened in plain English

Include a mix: normal operations, security violations (BLOCKED), limit violations (BLOCKED), edge cases.

Return ONLY the JSON array."""
        
        response = await self.provider.send_message(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=4000,
            temperature=0.4
        )
        
        try:
            clean = response.strip()
            if "```" in clean:
                parts = clean.split("```")
                clean = parts[1]
                if clean.startswith("json"):
                    clean = clean[4:]
            examples = json.loads(clean)
            
            # Use the secondary Hardware Language Model to produce training code for the small model
            from engine.training.hardware_bridge import hardware_bridge
            import asyncio
            for ex in examples:
                if "PASSED" in str(ex.get("rule_check", "")):
                    ex["assembly"] = await asyncio.to_thread(
                        hardware_bridge.generate_assembly, ex.get("instruction", "Unknown")
                    )
                else:
                    ex["assembly"] = "; BLOCKED\n; Rule violation detected"
        except Exception as e:
            print(f"Data generation processing error: {e}")
            examples = self._get_fallback_examples()
        
        # Save as JSONL
        async with aiofiles.open(self.output_path, "w", encoding="utf-8") as f:
            content = "".join(json.dumps(ex) + "\n" for ex in examples)
            await f.write(content)
        
        await self.broadcast({
            "type": "training_data_ready",
            "count": len(examples),
            "project_id": self.project_id
        })
        
        return examples
    
    def _get_fallback_examples(self) -> List[dict]:
        return [
            {"instruction": "Process a standard operation", "assembly": "mov eax, 1\nmov ebx, [data]\nadd eax, ebx\nmov [result], eax", "rule_check": "PASSED", "result": "Operation completed successfully"},
            {"instruction": "Attempt unauthorized operation", "assembly": "; BLOCKED\n; Rule violation detected", "rule_check": "BLOCKED: Security rule violated", "result": "Action blocked by security rules"},
            {"instruction": "Generate daily report", "assembly": "mov eax, [report_flag]\nmov [output], eax", "rule_check": "PASSED", "result": "Report generated successfully"},
        ]
