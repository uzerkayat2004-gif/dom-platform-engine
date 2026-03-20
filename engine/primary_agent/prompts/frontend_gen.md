Generate a complete, premium HTML frontend for this app.

App domain: {domain}
Rule files: {rule_files}

Requirements:
- Pure HTML and CSS only — no frameworks, no libraries
- Minimal JavaScript for fetch calls to localhost:5000/process only — no application logic in the frontend
- Every button sends a plain English instruction as JSON: fetch('/process', {method:'POST', body: JSON.stringify({instruction: "..."})})
- Design: dark theme, professional, premium SaaS quality
- Every operation the skills.md file permits must have a corresponding UI element
- Include a visible status area that shows the last response from the DOM server

Return the complete HTML file as a single string. Include all CSS inside a <style> tag. No external dependencies.
