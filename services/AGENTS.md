# AGENTS.md - Services Layer

## Package Identity

- **Purpose**: Business logic services (clipboard, file watching, metadata, previews)
- **Pattern**: Singleton classes with `@classmethod` methods
- **Data persistence**: JSON files (`file_tags.json`)

---

## Key Files

| File | Purpose | Pattern |
|------|---------|---------|
| `metadata_service.py` | File tagging (colors, notes) | Singleton with JSON persistence |
| `clipboard.py` | Internal file clipboard | Singleton with class variables |
| `watchdog_service.py` | File system monitoring | Event handler pattern |
| `preview/excel_preview.py` | Excel file data extraction | Utility function |

---

## Patterns & Conventions

### Singleton Service Pattern
```python
# ✅ Use classmethod for singleton services (from metadata_service.py)
class MetadataService:
    _tags = {}  # Class-level storage
    
    @classmethod
    def set_tag(cls, path, color=None, note=None):
        if path not in cls._tags:
            cls._tags[path] = {}
        if color:
            cls._tags[path]["color"] = color
        cls.save_tags()
```

### Clipboard Pattern
```python
# ✅ Simple singleton from clipboard.py
class InternalClipboard:
    file_path = None
    operation = None
    source_panel = None
    
    @classmethod
    def set(cls, path, op, panel):
        cls.file_path = path
        cls.operation = op
        cls.source_panel = panel
```

### File Watcher Pattern
```python
# ✅ Debounced event handler from watchdog_service.py
class FolderChangeHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback
        self.last_refresh = 0
    
    def on_any_event(self, event):
        if time.time() - self.last_refresh > 1.0:
            self.callback()
            self.last_refresh = time.time()
```

---

## Touch Points

- **Tag storage**: `file_tags.json` in project root
- **Tag colors**: `red`, `green`, `yellow` (see `ui/styles.py` for hex values)
- **Clipboard clear**: Must call `source_panel.clear_clipboard_indicator()`

---

## JIT Index Hints

```bash
# Find service class definitions
rg -n "class \w+:" services/

# Find classmethod definitions
rg -n "@classmethod" services/

# Find JSON file operations
rg -n "json\.(load|dump)" services/

# Find watchdog usage
rg -n "FileSystemEventHandler|Observer" services/
```

---

## Common Gotchas

1. **MetadataService.load_tags()**: Must be called before `get_tag()` works
2. **Clipboard source_panel**: Can be `None` - always check before calling methods
3. **Watchdog debounce**: 1 second minimum between refreshes to prevent spam
4. **Excel preview**: Requires optional `pandas` and `openpyxl` packages

---

## Sub-packages

### `preview/`
- `excel_preview.py`: Reads Excel with pandas, returns `(columns, rows)`
- Optional dependency: fails gracefully if pandas not installed

---

## Pre-PR Checks

```bash
python -c "from services.metadata_service import MetadataService; from services.clipboard import InternalClipboard; print('Services imports OK')"
```
