# 🤝 Contributing to Fleet Agent IDE

Thank you for your interest in contributing to **Fleet Agent IDE**! We are committed to building a world-class, high-performance open source orchestrator for autonomous coding fleets.

---

## 🧭 Code of Conduct

We follow standard open-source community standards: be welcoming, constructive, respectful, and open to collaboration.

---

## 🛠️ Getting Started

### 1. Fork & Clone
```bash
git clone https://github.com/your-username/fleet-agent-ide.git
cd fleet-agent-ide
```

### 2. Environment Setup
```bash
python -m venv .venv
# On Windows:
.venv\Scripts\Activate.ps1
# On Linux/macOS:
source .venv/bin/activate

# Install all subpackages in editable mode
pip install -e "./contracts"
pip install -e "./backend"
pip install -e "./cli"
pip install pytest pytest-asyncio ruff mypy
```

### 3. Frontend Setup
```bash
cd web
npm install
npm run dev
```

---

## 📋 Pull Request Guidelines

1. **Create a topic branch**:
   ```bash
   git checkout -b feat/your-feature-name
   ```
2. **Follow Conventional Commits**:
   - `feat(worktree): add auto-prune on shutdown`
   - `fix(web): resolve Monaco diff auto-scrolling`
   - `docs(adr): document tree-sitter AST parser`
3. **Run Linters and Tests**:
   ```bash
   ruff check .
   ruff format .
   pytest
   cd web && npm run build
   ```
4. **Submit your PR** with a clear explanation of changes, screenshots for UI modifications, and test evidence.

---

## 💡 Areas Where We Love Help

- 🗺️ **Tree-Sitter RepoMap integration** for AST-level symbol extraction.
- ✂️ **Surgical Search/Replace Patcher** with fuzzy line matching.
- 🔀 **Automated Merge Queue** with conflict resolution agents.
- 🔌 **New Agent Harnesses** (Claude Code CLI driver, Aider harness, Pi ACP driver).
