# Config Layer - CLAUDE.md

**Technology**: Pure Python with JSON persistence
**Entry Point**: `manager.py`
**Parent Context**: This extends [../CLAUDE.md](../CLAUDE.md)

---

## Development Commands

```bash
# Import check
python -c "from config.manager import ConfigManager; print('Config OK')"

# Test config operations
python -m unittest tests.verify_features.TestWorkDashboardFeatures.test_config_manager
```

---

## Architecture

### Directory Structure

```
config/
├── __init__.py    # Package init
└── manager.py     # ConfigManager class ★
```

### Code Pattern

```python
# ✅ From manager.py - Static methods for JSON persistence
import os
import json

CONFIG_FILE = "dashboard_config.json"

class ConfigManager:
    @staticmethod
    def load_config():
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError) as e:
                print(f"Error loading config: {e}")
                return {"workspaces": {}}
        return {"workspaces": {}}

    @staticmethod
    def save_config(data):
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Error saving config: {e}")
```

---

## Config File Structure

### `dashboard_config.json`

```json
{
  "num_panels": 6,
  "layout_mode": "G",
  "theme_name": "Dark",
  "font_size": 16,
  "1": "/path/to/folder1",
  "2": "/path/to/folder2",
  "workspaces": {
    "workspace_name": {
      "num_panels": 4,
      "layout_mode": "V",
      "paths": {
        "1": "/path",
        "2": "/path"
      }
    }
  }
}
```

### Config Keys

| Key | Type | Purpose |
|-----|------|---------|
| `num_panels` | int | Number of panels (2-9) |
| `layout_mode` | str | "G" (grid), "V" (vertical), "H" (horizontal) |
| `theme_name` | str | "Light" or "Dark" |
| `font_size` | int | Base font size (10-28) |
| `"1"`, `"2"`, ... | str | Panel folder paths |
| `workspaces` | dict | Saved workspace configurations |

---

## Key Files

| File | Class | Purpose |
|------|-------|---------|
| `manager.py` | `ConfigManager` | JSON config persistence |

### Data Location

- **Config file**: `dashboard_config.json` (project root)
- **Default value**: `{"workspaces": {}}`

---

## Quick Search Commands

```bash
# Find config file references
rg -n "CONFIG_FILE|dashboard_config" .

# Find config usage in main app
rg -n "config_data" work_dashboard.py ui/

# Find save/load calls
rg -n "save_config|load_config" .
```

---

## Common Gotchas

1. **Graceful Degradation**:
   - Returns empty config `{"workspaces": {}}` on any error
   - Never throws exceptions to caller

2. **Duplicate Implementation**:
   - `ConfigManager` also exists in `work_dashboard.py` lines 15-28
   - Both implementations are similar, but main app uses its own

3. **No Validation**:
   - Config loaded as-is
   - Invalid keys silently ignored
   - No schema validation

4. **Personal Data**:
   - Contains user file paths
   - Should NOT be committed to git

5. **File Location**:
   - `CONFIG_FILE` is relative path "dashboard_config.json"
   - Created in current working directory

---

## Testing

```bash
# Test ConfigManager
python -m unittest tests.verify_features.TestWorkDashboardFeatures.test_config_manager
```

Note: Test uses mocked config file location to avoid modifying real config.
