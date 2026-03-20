# DOM Platform — Category C Engine

> The world's first Category C app builder. Build any app in plain English. Own your AI completely.

## What is Category C?

**Category A** — Traditional coding. Humans write code by hand.  
**Category B** — No-code. Drag blocks, code hidden underneath.  
**Category C** — No code at all. Describe your app in plain English. A domain-specific AI model becomes your app's brain. Runs locally. Works offline. Yours forever.

## Quick Start

```bash
npm install
npm run tauri dev
```

## Tech Stack

- **Desktop Shell**: Tauri (Rust)
- **Frontend**: HTML / CSS / JavaScript
- **Engine**: Python (Primary Agent + Training + DOM Server)
- **AI Models**: Pluggable (Claude, GPT, Groq, etc.) + LLM4Binary (local)

## Project Structure

```
src/          → Frontend UI
src-tauri/    → Tauri/Rust shell
engine/       → Python Category C Engine
projects/     → User projects
config/       → Platform config
```

## License

Proprietary. All rights reserved.
