# 🛠️ Development & Contribution Guide

Welcome to the **Fleet Agent IDE** development guide.

---

## 📋 Prerequisites

- **Python 3.11+**
- **Git 2.20+** (supporting `git worktree`)
- Modern terminal (Windows Terminal, iTerm2, Alacritty)

---

## 🚀 Setting Up the Monorepo

```bash
# 1. Clone the repository
git clone https://github.com/your-org/fleet-agent-ide.git
cd fleet-agent-ide

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install packages in editable development mode
pip install -e "contracts/"
pip install -e "backend/"
pip install -e "cli/"
```

---

## 🧪 Running Locally

```bash
# Terminal 1: Start Daemon
fleet daemon --port 8000 --reload

# Terminal 2: Dispatch a task
fleet run "Add comprehensive unit tests for worktree manager" --title "Worktree Tests"

# Terminal 2: Monitor status
fleet status
fleet worktrees
```
