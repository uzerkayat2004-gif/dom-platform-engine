"""
Rule Files Generator
Creates and manages the four constitutional rule files for each project.
These rule files become the DNA of the DOM model.
"""

import json
from pathlib import Path
from typing import List

class RuleGenerator:
    
    RULE_FILES = ["security_md", "behavior_md", "limits_md", "skills_md"]
    FILE_NAMES = {
        "security_md": "security.md",
        "behavior_md": "behavior.md",
        "limits_md": "limits.md",
        "skills_md": "skills.md"
    }
    
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.rules_dir = Path(f"projects/{project_id}/rules")
        self.rules_dir.mkdir(parents=True, exist_ok=True)
    
    def save(self, rule_files: dict) -> List[str]:
        """Save all four rule files. Returns list of saved filenames."""
        saved = []
        for key, filename in self.FILE_NAMES.items():
            if key in rule_files:
                file_path = self.rules_dir / filename
                file_path.write_text(rule_files[key])
                saved.append(filename)
        return saved
    
    def read_all(self) -> dict:
        """Read all existing rule files."""
        result = {}
        for key, filename in self.FILE_NAMES.items():
            file_path = self.rules_dir / filename
            if file_path.exists():
                result[key] = file_path.read_text()
        return result
    
    def read(self, rule_type: str) -> str:
        """Read a single rule file by key (e.g. 'security_md')."""
        filename = self.FILE_NAMES.get(rule_type, "")
        file_path = self.rules_dir / filename
        if file_path.exists():
            return file_path.read_text()
        return ""
    
    def validate(self) -> dict:
        """Validate that all four rule files exist and are non-empty."""
        results = {}
        for key, filename in self.FILE_NAMES.items():
            file_path = self.rules_dir / filename
            results[key] = file_path.exists() and file_path.stat().st_size > 0
        results["all_valid"] = all(v for k, v in results.items() if k != "all_valid")
        return results
    
    def get_combined_rules(self) -> str:
        """Return all rule files combined into one string for model training."""
        all_rules = self.read_all()
        combined = ""
        for key, filename in self.FILE_NAMES.items():
            if key in all_rules:
                combined += f"=== {filename} ===\n{all_rules[key]}\n\n"
        return combined
