# CLAUDE.md — Fleet Agent IDE

Guidelines and quick commands for Claude Code and related tooling.

## 🚀 Common Commands

```bash
# Environment Setup
python -m venv .venv
.venv\Scripts\Activate.ps1   # Windows
source .venv/bin/activate    # Linux/macOS

# Install in Editable Mode
pip install -e "./contracts"
pip install -e "./backend"
pip install -e "./cli"

# Run Daemon
fleet daemon --port 8000 --reload

# Run CLI Commands
fleet run "Task description" --title "Task Title"
fleet status
fleet worktrees

# Run Frontend Dashboard
cd web
npm install
npm run dev
```

## 🏗️ Architecture Conventions

- **Language & Runtime**: Python 3.11+ (Backend/CLI), TypeScript + React 18 (Frontend).
- **Core Abstractions**:
  - `WorktreeManager`: Creates `agent/<task-id>` branches in `.fleet/worktrees/<task-id>`.
  - `LangGraphHarness`: Manages reflective `inspect -> execute -> validate -> reflect` loops.
  - `EventBus`: Broadcasts `FleetEvent` instances via Server-Sent Events (`/api/events/sse`).
- **Code Style**: Ruff 100 char limit, explicit Pydantic type annotations, clean imports.
