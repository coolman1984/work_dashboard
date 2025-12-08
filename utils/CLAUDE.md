# Utils Layer - CLAUDE.md

**Technology**: Pure Python (stdlib only)
**Entry Point**: Import individual utilities as needed
**Parent Context**: This extends [../CLAUDE.md](../CLAUDE.md)

---

## Development Commands

```bash
# Import check
python -c "from utils.files import open_path, get_file_info; from utils.debounce import Debouncer; print('Utils OK')"
```

---

## Architecture

### Directory Structure

```
utils/
├── __init__.py     # Package init
├── files.py        # File system operations ★
└── debounce.py     # Search input debouncing ★
```

### Code Organization Patterns

#### File Operations

```python
# ✅ From files.py - Platform-specific file opening
import os
from tkinter import messagebox

def open_path(path):
    try:
        os.startfile(path)  # Windows-specific
    except OSError as e:
        messagebox.showerror("Error", f"Could not open path:\n{e}")

def get_file_info(filepath):
    try:
        stats = os.stat(filepath)
        size_mb = stats.st_size / (1024 * 1024)
        mod_time = datetime.datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M')
        return stats.st_size, size_mb, mod_time
    except:
        return 0, 0.0, "Unknown"
```

#### Debouncer Pattern

```python
# ✅ From debounce.py - Tkinter-compatible debouncing
class Debouncer:
    def __init__(self, widget, callback, delay=300):
        self.widget = widget      # Tkinter widget for after()
        self.callback = callback  # Function to call
        self.delay = delay        # Milliseconds
        self._timer_id = None

    def trigger(self):
        if self._timer_id:
            self.widget.after_cancel(self._timer_id)
        self._timer_id = self.widget.after(self.delay, self.callback)
```

---

## Usage Examples

### From `ui/folder_card.py`

```python
from utils.files import open_path, get_file_info
from utils.debounce import Debouncer

# Debounced search (lines 113-115)
self.search_debouncer = Debouncer(self, self.refresh_files, 300)
self.search_var.trace_add("write", lambda *args: self.search_debouncer.trigger())

# Get file info (line 414)
raw_size, size_mb, mod = get_file_info(full_path)

# Open file/folder (line 271)
open_path(self.current_path)
```

---

## Key Files

| File | Functions | Purpose |
|------|-----------|---------|
| `files.py` | `open_path()`, `get_file_info()` | File operations |
| `debounce.py` | `Debouncer` class | Input debouncing |

---

## Quick Search Commands

```bash
# Find utility functions
rg -n "^def \w+" utils/

# Find utility classes
rg -n "^class \w+" utils/

# Find utils usage
rg -n "from utils" ui/ services/ work_dashboard.py
```

---

## Common Gotchas

1. **`open_path()` is Windows-only**:
   - Uses `os.startfile()` which doesn't exist on Linux/Mac
   - For cross-platform, would need `subprocess` with platform detection

2. **`Debouncer` requires tkinter widget**:
   - Uses `widget.after()` for scheduling
   - Cannot be used outside of tkinter context

3. **File info error handling**:
   - Returns `(0, 0.0, "Unknown")` on any exception
   - Silently handles all errors

4. **Import order**:
   - `files.py` imports `messagebox` from tkinter
   - Only use after tkinter is initialized

---

## Testing

Utils are tested indirectly through manual testing of the application.
No dedicated unit tests for utils currently.
