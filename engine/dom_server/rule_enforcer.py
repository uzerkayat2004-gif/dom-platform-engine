"""
Runtime Rule Enforcer
Checks every incoming instruction against the project's rule files
BEFORE the DOM model executes anything.
This is what makes the Glass Box demo so powerful —
security is enforced before execution, not after.
"""

import re
from engine.rules.generator import RuleGenerator

class RuleEnforcer:
    
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.rule_gen = RuleGenerator(project_id)
        self._load_rules()
    
    def _load_rules(self):
        """Load all rule files into memory."""
        rules = self.rule_gen.read_all()
        self.security_rules = rules.get("security_md", "")
        self.limits_rules = rules.get("limits_md", "")
        self.behavior_rules = rules.get("behavior_md", "")
        self.skills_rules = rules.get("skills_md", "")
    
    def check(self, instruction: str) -> dict:
        """
        Check instruction against all rule files.
        Returns: {allowed: bool, reason: str, rule_file: str, rule_number: str}
        """
        instruction_lower = instruction.lower()
        
        # Check price limits from limits.md
        price_matches = re.findall(r'(\d+)\s*rupees?', instruction_lower)
        for price_str in price_matches:
            price = int(price_str)
            # Extract limit from limits.md
            limit_match = re.search(
                r'maximum single (?:item |transaction )?(?:price|value)[:\s]+(?:rs\.?)?(\d+)',
                self.limits_rules.lower()
            )
            limit = int(limit_match.group(1)) if limit_match else 10000
            if price > limit:
                return {
                    "allowed": False,
                    "reason": f"Item price Rs.{price} exceeds Rs.{limit:,} limit",
                    "rule_file": "limits.md",
                    "rule_number": "Rule 1"
                }
        
        # Check discount limits
        discount_matches = re.findall(
            r'(\d+)\s*(?:percent|%)',
            instruction_lower
        )
        is_discount = any(
            kw in instruction_lower
            for kw in ['discount', 'reduce', 'off', 'percent off']
        )
        if discount_matches and is_discount:
            discount = int(discount_matches[0])
            # Extract limit from security or limits rules
            discount_limit_match = re.search(
                r'maximum discount[^:]*:\s*(\d+)%',
                (self.limits_rules + self.security_rules).lower()
            )
            discount_limit = int(discount_limit_match.group(1)) if discount_limit_match else 30
            if discount > discount_limit:
                return {
                    "allowed": False,
                    "reason": f"{discount}% discount exceeds {discount_limit}% maximum",
                    "rule_file": "security.md",
                    "rule_number": "Rule 2"
                }
        
        # Check skill permissions — is this action in skills.md?
        allowed_keywords = self._extract_skill_keywords()
        action_words = re.findall(r'\b\w+\b', instruction_lower)
        has_permission = any(
            kw in instruction_lower for kw in allowed_keywords
        )
        if not has_permission and len(instruction.split()) > 2:
            return {
                "allowed": False,
                "reason": "Action not found in skills.md — permission denied",
                "rule_file": "skills.md",
                "rule_number": "Permission check"
            }
        
        return {
            "allowed": True,
            "reason": "All rule checks passed",
            "rule_file": None,
            "rule_number": None
        }
    
    def _extract_skill_keywords(self) -> list:
        """Extract action keywords from skills.md."""
        default_keywords = [
            "add", "remove", "update", "delete", "create", "get", "show",
            "process", "send", "apply", "generate", "calculate", "view",
            "order", "payment", "discount", "kitchen", "report", "new",
            "cancel", "complete", "list", "search", "print", "reset"
        ]
        if not self.skills_rules:
            return default_keywords
        
        # Extract verbs from skills.md
        skill_lines = [
            l.lower() for l in self.skills_rules.split("\n")
            if l.strip().startswith("skill")
        ]
        keywords = list(default_keywords)
        word_pattern = re.compile(r'\b\w+\b')
        for line in skill_lines:
            words = word_pattern.findall(line)
            keywords.extend([w for w in words if len(w) > 3])
        
        return list(set(keywords))
    
    def reload(self):
        """Reload rules from disk (called after rule file updates)."""
        self._load_rules()
