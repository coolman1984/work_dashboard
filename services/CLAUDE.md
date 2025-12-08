# Services Layer - CLAUDE.md

**Technology**: Pure Python, watchdog library for file monitoring
**Entry Point**: Import individual services as needed
**Parent Context**: This extends [../CLAUDE.md](../CLAUDE.md)

---

## Development Commands

```bash
# Import check
python -c "from services.metadata_service import MetadataService; from services.clipboard import InternalClipboard; print('Services OK')"

# Run service tests
python -m unittest tests.verify_features.TestWorkDashboardFeatures.test_metadata_service
python -m unittest tests.verify_features.TestWorkDashboardFeatures.test_clipboard_service
```

---

## Architecture

### Directory Structure

```
services/
├── __init__.py              # Package init
├── metadata_service.py      # File tagging (colors, notes) ★
├── clipboard.py             # Internal file clipboard ★
├── watchdog_service.py      # File system monitoring
└── preview/
    ├── __init__.py
    └── excel_preview.py     # Excel data extraction
```

### Code Organization Patterns

#### Singleton Service Pattern (CRITICAL)

All services use class-level state with `@classmethod`:

```python
# ✅ From metadata_service.py - CORRECT pattern
class MetadataService:
    _tags = {}  # Class-level storage
    
    @classmethod
    def load_tags(cls):
        # Load from file_tags.json
        
    @classmethod
    def set_tag(cls, path, color=None, note=None):
        if path not in cls._tags:
            cls._tags[path] = {}
        if color:
            cls._tags[path]["color"] = color
        cls.save_tags()
    
    @classmethod
    def get_tag(cls, path):
        return cls._tags.get(path, {})
```

```python
# ✅ From clipboard.py - Simple singleton
class InternalClipboard:
    file_path = None
    operation = None  # 'copy' or 'cut'
    source_panel = None
    
    @classmethod
    def set(cls, path, op, panel):
        cls.file_path = path
        cls.operation = op
        cls.source_panel = panel
    
    @classmethod
    def get(cls):
        return cls.file_path, cls.operation
    
    @classmethod
    def has_data(cls):
        return cls.file_path is not None
```

#### Event Handler Pattern

```python
# ✅ From watchdog_service.py - Debounced file watcher
from watchdog.events import FileSystemEventHandler

class FolderChangeHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback
        self.last_refresh = 0
    
    def on_any_event(self, event):
        if time.time() - self.last_refresh > 1.0:
            self.callback()
            self.last_refresh = time.time()
```

#### Optional Dependency Pattern

```python
# ✅ From preview/excel_preview.py - Graceful optional import
try:
    import pandas as pd
except ImportError:
    pd = None

def get_excel_data(filepath):
    if pd is None:
        raise ImportError("pandas/openpyxl not installed")
    # ... rest of implementation
```

---

## Key Files

### Core Services

| File | Class | Purpose |
|------|-------|---------|
| `metadata_service.py` | `MetadataService` | File tagging (color, notes) |
| `clipboard.py` | `InternalClipboard` | Copy/cut/paste operations |
| `watchdog_service.py` | `FolderChangeHandler` | File system monitoring |

### Data Storage

- **`file_tags.json`** (project root): Persists file metadata
  ```json
  {
    "/path/to/file.xlsx": {
      "color": "red",
      "note": "Important document"
    }
  }
  ```

### Touch Points

| Purpose | Location |
|---------|----------|
| Tag colors | `red`, `green`, `yellow` (see `ui/styles.py` for hex) |
| Load tags | Must call `MetadataService.load_tags()` before use |
| Clipboard clear | Call `source_panel.clear_clipboard_indicator()` |

---

## Quick Search Commands

```bash
# Find service classes
rg -n "^class \w+:" services/

# Find classmethod definitions
rg -n "@classmethod" services/

# Find JSON operations
rg -n "json\.(load|dump)" services/

# Find watchdog usage
rg -n "FileSystemEventHandler|Observer" services/

# Find service imports from UI
rg -n "from services" ui/ work_dashboard.py
```

---

## Common Gotchas

1. **MetadataService Initialization**: 
   - **MUST** call `MetadataService.load_tags()` before `get_tag()` works
   - Called in `folder_card.py` line 163

2. **Clipboard Source Panel**:
   - `source_panel` can be `None` - always check before calling methods
   - See `clipboard.py` line 9

3. **Watchdog Debounce**:
   - 1-second minimum between refreshes to prevent spam
   - See `watchdog_service.py` lines 6-7

4. **Excel Preview**:
   - Requires optional `pandas` and `openpyxl` packages
   - Fails gracefully if not installed

5. **File Paths in Tags**:
   - Uses absolute paths as keys
   - Paths are OS-specific (Windows backslashes)

---

## Testing

```bash
# Test MetadataService
python -m unittest tests.verify_features.TestWorkDashboardFeatures.test_metadata_service

# Test Clipboard
python -m unittest tests.verify_features.TestWorkDashboardFeatures.test_clipboard_service
```
