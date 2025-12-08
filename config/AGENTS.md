# AGENTS.md - Config Layer

## Package Identity

- **Purpose**: Application configuration persistence
- **Pattern**: Static methods for JSON file operations
- **Storage**: `dashboard_config.json` in project root

---

## Key Files

| File | Purpose |
|------|---------|
| `manager.py` | ConfigManager class for load/save operations |

---

## Patterns & Conventions

### Config Manager Pattern
```python
# ✅ From config/manager.py
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
      "paths": {"1": "/path", "2": "/path"}
    }
  }
}
```

---

## Touch Points

- **Config file location**: `dashboard_config.json` (project root)
- **Default empty config**: `{"workspaces": {}}`
- **Panel paths**: Stored as string keys `"1"`, `"2"`, etc.

---

## JIT Index Hints

```bash
# Find config file references
rg -n "CONFIG_FILE|dashboard_config" .

# Find config usage in main app
rg -n "config_data" work_dashboard.py ui/
```

---

## Common Gotchas

1. **Graceful degradation**: Returns empty config on file errors
2. **Duplicate implementation**: `ConfigManager` also exists in `work_dashboard.py`
3. **No validation**: Config loaded as-is, invalid keys silently ignored

---

## Pre-PR Checks

```bash
python -c "from config.manager import ConfigManager; print('Config imports OK')"
```
