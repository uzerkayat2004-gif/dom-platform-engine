Based on the complete conversation below, generate the four rule files for this app.

Return ONLY a valid JSON object with these exact keys:
- security_md
- behavior_md
- limits_md
- skills_md

Each value is a string containing the full content of that rule file.

Requirements for each file:
- security_md: 8 to 12 specific, measurable security rules. Each rule on its own line starting with "Rule N:"
- behavior_md: 6 to 10 behavioral rules about how the app must always act. Each rule on its own line starting with "Rule N:"
- limits_md: 4 to 8 hard numerical limits that cannot be crossed. Each rule on its own line starting with "Rule N:"
- skills_md: 6 to 12 specific actions the app is permitted to perform. Each skill on its own line starting with "Skill N:"

Conversation context:
{conversation}

Return ONLY the JSON object. No explanation. No markdown. No code blocks.
