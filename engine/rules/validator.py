"""Validates rule file structure and content quality."""

from engine.rules.generator import RuleGenerator

class RuleValidator:
    
    def __init__(self, project_id: str):
        self.generator = RuleGenerator(project_id)
    
    def validate_completeness(self) -> dict:
        return self.generator.validate()
    
    def validate_content(self) -> dict:
        rules = self.generator.read_all()
        issues = []
        
        for key, content in rules.items():
            lines = [l.strip() for l in content.split("\n") if l.strip()]
            rule_lines = [l for l in lines if l.startswith("Rule ") or l.startswith("Skill ")]
            if len(rule_lines) < 3:
                issues.append(f"{key} has fewer than 3 rules — needs more detail")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues
        }
