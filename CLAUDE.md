# Work Dashboard

## Overview

- **Type**: Single Python desktop application
- **Stack**: Python 3.8+, CustomTkinter (GUI), watchdog (file monitoring), tkinter/ttk
- **Architecture**: Modular MVC-like structure with UI, Services, Utils, and Config layers
- **Purpose**: Multi-panel file management with tagging, search, and workspace persistence

This CLAUDE.md is the authoritative source for development guidelines.
Subdirectories contain specialized CLAUDE.md files that extend these rules.

---

## Universal Development Rules

### Code Quality (MUST)

- **MUST** follow PEP 8 style guidelines
- **MUST** use type hints for function signatures where practical
- **MUST** include docstrings for public classes and methods
- **MUST** test changes manually before committing
- **MUST NOT** commit personal file paths in code or configs
- **MUST NOT** commit API keys, tokens, or credentials

### Best Practices (SHOULD)

- **SHOULD** use snake_case for functions/variables, PascalCase for classes
- **SHOULD** prefer composition over deep inheritance
- **SHOULD** keep functions under 50 lines
- **SHOULD** use `@classmethod` for singleton-style services
- **SHOULD** handle exceptions gracefully with user-friendly messages

### Anti-Patterns (MUST NOT)

- **MUST NOT** mix `grid()` and `pack()` in the same container
- **MUST NOT** hardcode colors - use `ui/styles.py` constants
- **MUST NOT** perform file operations on the main thread without protection
- **MUST NOT** leave bare `except:` clauses without logging

---

## Core Commands

### Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run application
python work_dashboard.py

# Run tests
python -m unittest tests/verify_features.py

# Run specific test class
python -m unittest tests.verify_features.TestWorkDashboardFeatures
```

### Build & Distribution

```bash
# Build executable (requires PyInstaller)
pip install pyinstaller
pyinstaller work_dashboard.spec

# Output: dist/WorkDashboard.exe
```

### Quality Gates (run before commit)

```bash
python -m py_compile work_dashboard.py && python -m unittest tests/verify_features.py
```

---

## Project Structure

### Core Files

- **`work_dashboard.py`** → Main application entry point (306 lines)
  - Contains: `WorkDashboard` class, `ConfigManager`
  - Run: `python work_dashboard.py`

- **`main.py`** → Alternative entry point (imports work_dashboard)

### Layers

- **`ui/`** → GUI components ([see ui/CLAUDE.md](ui/CLAUDE.md))
  - `folder_card.py` - Main panel component (646 lines)
  - `dashboard.py` - Alternative dashboard implementation
  - `quick_look.py` - File preview window
  - `styles.py` - Themes and color constants

- **`services/`** → Business logic ([see services/CLAUDE.md](services/CLAUDE.md))
  - `metadata_service.py` - File tagging system
  - `clipboard.py` - Internal clipboard
  - `watchdog_service.py` - File system monitoring
  - `preview/` - File preview handlers

- **`utils/`** → Helpers ([see utils/CLAUDE.md](utils/CLAUDE.md))
  - `files.py` - File operations
  - `debounce.py` - Input debouncing

- **`config/`** → Configuration ([see config/CLAUDE.md](config/CLAUDE.md))
  - `manager.py` - JSON persistence

### Data Files

- **`dashboard_config.json`** → User settings, workspaces, panel paths
- **`file_tags.json`** → File metadata (colors, notes)

### Assets

- **`icons/`** → File type icons (PNG format)
- **`icon.svg`** → Application icon

### Tests

- **`tests/verify_features.py`** → Unit tests for core features

---

## Quick Find Commands

### Code Navigation

```bash
# Find a class definition
rg -n "^class \w+" *.py ui/*.py services/*.py utils/*.py config/*.py

# Find a method in a specific class
rg -n "def \w+" ui/folder_card.py

# Find all imports of a module
rg -n "from services" ui/ work_dashboard.py

# Find theme/color usage
rg -n "THEMES|ACCENT_COLORS|TYPE_COLORS" .

# Find keyboard bindings
rg -n "\.bind\(" ui/
```

### Dependencies

```bash
# Check what a module imports
rg -n "^import|^from" ui/folder_card.py

# Find usages of a service
rg -n "MetadataService|InternalClipboard" ui/ work_dashboard.py
```

---

## Security Guidelines

### Secrets Management

- **NEVER** commit personal file paths (they're in `dashboard_config.json`)
- **NEVER** hardcode credentials or API keys
- Configuration files are local-only, not part of distribution

### Safe Operations

- Confirm before bulk delete operations
- Test file operations in safe directories first
- Keep `file_tags.json` backed up (contains user metadata)

### Files to Protect

- `dashboard_config.json` - Contains personal paths
- `file_tags.json` - Contains user annotations
- `.env` files - If added for future features

---

## Git Workflow

- Branch from `main` for features: `feature/description`
- Use descriptive commit messages: `Add feature`, `Fix bug in X`, `Refactor Y`
- Test application before committing
- Keep commits focused and atomic

---

## Testing Requirements

- **Unit tests**: `tests/verify_features.py` covers core services
- **Manual testing**: Always run application after changes
- **Coverage areas**:
  - ConfigManager (save/load)
  - MetadataService (tags, notes)
  - InternalClipboard (copy, cut, paste)
  - File operations (via mock)

### Running Tests

```bash
# All tests
python -m unittest tests/verify_features.py -v

# Specific test
python -m unittest tests.verify_features.TestWorkDashboardFeatures.test_metadata_service
```

---

## Available Tools

You have access to:
- Standard Python tools (pip, python)
- Git for version control
- ripgrep (`rg`) for code search
- PyInstaller for building executables

### Tool Permissions

- ✅ Read any file in project
- ✅ Write code files (.py, .md)
- ✅ Run tests and linters
- ✅ Create new files
- ⚠️ Edit JSON configs (ask first - may contain user data)
- ❌ Delete user data files (ask first)
- ❌ Run destructive OS commands (ask first)

---

## Specialized Context

When working in specific directories, refer to their CLAUDE.md:

| Directory | Purpose | Link |
|-----------|---------|------|
| `ui/` | GUI components | [ui/CLAUDE.md](ui/CLAUDE.md) |
| `services/` | Business logic | [services/CLAUDE.md](services/CLAUDE.md) |
| `utils/` | Utility functions | [utils/CLAUDE.md](utils/CLAUDE.md) |
| `config/` | Configuration | [config/CLAUDE.md](config/CLAUDE.md) |

These files provide detailed, context-specific guidance.

---

## Common Gotchas

1. **Thread Safety**: Use `widget.after(ms, callback)` for UI updates from watchdog
2. **Treeview Styling**: Use `ttk.Style()` not CustomTkinter for Treeview
3. **Icon References**: Keep icon PhotoImage objects alive to prevent garbage collection
4. **Focus Mode**: Destroys and recreates container - see `toggle_focus_mode()`
5. **Config Duplication**: `ConfigManager` exists in both `work_dashboard.py` and `config/manager.py`
