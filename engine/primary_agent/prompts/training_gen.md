Generate {count} training examples for a DOM model fine-tuned on this domain.

Rule files active:
{rule_files}

Return ONLY a JSON array. Each item must have exactly these fields:
- instruction: a realistic plain English command a user would give this app
- assembly: realistic x86 assembly that would execute this instruction
- rule_check: "PASSED" or "BLOCKED: [specific rule violated]"
- result: plain English description of what happened

Distribution:
- 40% normal operations that pass all rules
- 20% operations that get blocked by security rules
- 20% operations that get blocked by limits rules
- 20% edge cases and boundary conditions

Return ONLY the JSON array. No explanation. No markdown fences.
