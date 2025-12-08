# AGENTS.md - Work Dashboard

## Project Snapshot

- **Type**: Single Python desktop application
- **Stack**: Python 3.8+, CustomTkinter (GUI), watchdog (file monitoring)
- **Purpose**: Multi-panel file management with tagging, search, and workspace persistence
- **Sub-packages**: `ui/`, `services/`, `utils/`, `config/` each have their own AGENTS.md

---

## Root Setup Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run application
python work_dashboard.py

# Run tests
python -m pytest tests/ -v
# OR
python -m unittest tests/verify_features.py

# Build executable (requires PyInstaller)
pyinstaller work_dashboard.spec
```

---

## Universal Conventions

- **Code Style**: PEP 8, use type hints where practical
- **Naming**: snake_case for functions/variables, PascalCase for classes
- **Imports**: Standard library → Third-party → Local imports
- **Line Length**: Prefer <100 characters
- **Comments**: Use docstrings for public methods, inline comments sparingly

---

## Security & Secrets

- **No secrets in code**: Configuration stored in `dashboard_config.json` (user-created)
- **User data**: File paths stored locally, `file_tags.json` contains user metadata
- **Never commit**: Personal config files with actual file paths

---

## JIT Index - Directory Map

### Package Structure

| Directory | Purpose | Details |
|-----------|---------|---------|
| `ui/` | GUI components | [see ui/AGENTS.md](ui/AGENTS.md) |
| `services/` | Business logic | [see services/AGENTS.md](services/AGENTS.md) |
| `utils/` | Helper utilities | [see utils/AGENTS.md](utils/AGENTS.md) |
| `config/` | Configuration management | [see config/AGENTS.md](config/AGENTS.md) |
| `tests/` | Unit tests | `verify_features.py` |
| `icons/` | File type icons | PNG files for treeview |
| `dist/` | Built executable | `WorkDashboard.exe` |

### Quick Find Commands

```bash
# Find a class definition
rg -n "class \w+" *.py ui/*.py services/*.py

# Find a method
rg -n "def \w+" ui/*.py services/*.py

# Find imports of a module
rg -n "from services" ui/*.py

# Find all TODO comments
rg -n "TODO|FIXME" --type py

# Find theme colors
rg -n "THEMES|ACCENT_COLORS" ui/
```

---

## Definition of Done

Before creating a PR:

1. `python -m unittest tests/verify_features.py` passes
2. Application runs without errors: `python work_dashboard.py`
3. No hardcoded personal file paths in code
4. New features documented in `README.md` if user-facing
