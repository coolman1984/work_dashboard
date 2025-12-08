# AGENTS.md - Utils Layer

## Package Identity

- **Purpose**: Shared utility functions and helper classes
- **Pattern**: Pure functions and simple utility classes
- **No external dependencies**: Uses only stdlib + tkinter

---

## Key Files

| File | Purpose | Functions |
|------|---------|-----------|
| `files.py` | File system operations | `open_path()`, `get_file_info()` |
| `debounce.py` | Search input debouncing | `Debouncer` class |

---

## Patterns & Conventions

### File Operations Pattern
```python
# ✅ Platform-specific file opening from files.py
def open_path(path):
    try:
        os.startfile(path)  # Windows-specific
    except OSError as e:
        messagebox.showerror("Error", f"Could not open path:\n{e}")
```

### File Info Pattern
```python
# ✅ Get file metadata from files.py
def get_file_info(filepath):
    stats = os.stat(filepath)
    size_mb = stats.st_size / (1024 * 1024)
    mod_time = datetime.datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M')
    return stats.st_size, size_mb, mod_time
```

### Debouncer Pattern
```python
# ✅ Tkinter-compatible debouncer from debounce.py
class Debouncer:
    def __init__(self, widget, callback, delay=300):
        self.widget = widget
        self.callback = callback
        self.delay = delay
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
```

---

## JIT Index Hints

```bash
# Find utility function definitions
rg -n "^def \w+" utils/

# Find utility class definitions
rg -n "^class \w+" utils/

# Find usages of utils in UI
rg -n "from utils" ui/ services/
```

---

## Common Gotchas

1. **`open_path()`**: Windows-only (`os.startfile`), needs platform check for Linux/Mac
2. **`Debouncer`**: Requires a tkinter widget for `after()` scheduling
3. **File info errors**: Returns `(0, 0.0, "Unknown")` on any exception

---

## Pre-PR Checks

```bash
python -c "from utils.files import open_path, get_file_info; from utils.debounce import Debouncer; print('Utils imports OK')"
```
