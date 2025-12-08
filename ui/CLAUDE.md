# UI Layer - CLAUDE.md

**Technology**: CustomTkinter (ctk) + ttk for Treeview widgets
**Entry Point**: `folder_card.py` (main panel component)
**Parent Context**: This extends [../CLAUDE.md](../CLAUDE.md)

---

## Development Commands

### Running the Application

```bash
# From project root
python work_dashboard.py

# Import check
python -c "from ui.folder_card import FolderCard; from ui.styles import THEMES; print('UI OK')"
```

### Pre-PR Checklist

```bash
python -m py_compile ui/folder_card.py ui/dashboard.py ui/quick_look.py ui/styles.py
```

---

## Architecture

### Directory Structure

```
ui/
├── __init__.py          # Package init (empty)
├── folder_card.py       # Main panel component (646 lines) ★
├── dashboard.py         # Alternative main window implementation
├── quick_look.py        # File preview popup window
└── styles.py            # Themes and color constants
```

### Code Organization Patterns

#### CustomTkinter Components

- ✅ **DO**: Inherit from `ctk.CTkFrame` or `ctk.CTkToplevel`
  - Example: `folder_card.py` line 16 → `class FolderCard(ctk.CTkFrame)`
  - Example: `quick_look.py` line 8 → `class QuickLookWindow(ctk.CTkToplevel)`

- ✅ **DO**: Use `grid()` layout with `weight` for responsive sizing
  - Example: `folder_card.py` lines 54-55:
    ```python
    self.grid_columnconfigure(0, weight=1)
    self.grid_rowconfigure(3, weight=1)
    ```

- ❌ **DON'T**: Mix `grid()` and `pack()` in the same container
- ❌ **DON'T**: Use class components from old tkinter patterns

#### Theming Pattern (CRITICAL)

```python
# ✅ ALWAYS use theme dict from styles.py
from ui.styles import THEMES, ACCENT_COLORS, TYPE_COLORS

t = THEMES[self.current_theme]
self.configure(fg_color=t["card"])
ctk.CTkLabel(self, text_color=t["text"])

# ❌ NEVER hardcode colors
self.configure(fg_color="#2c2c2c")  # BAD - use t["card"]
```

#### Treeview with Tags

```python
# ✅ From folder_card.py lines 216-221
from ui.styles import TAG_COLORS

for name, color in TAG_COLORS.items():
    self.tree.tag_configure(name, foreground="#000000", background=color)
```

#### Icon Loading Pattern

```python
# ✅ From folder_card.py lines 34-52
# Keep references alive to prevent garbage collection
self.icon_images = {}
for name, path in icon_paths.items():
    try:
        self.icon_images[name] = tk.PhotoImage(file=path)
    except:
        self.icon_images[name] = None
```

---

## Key Files

### Core Files (understand these first)

- `folder_card.py` → Main panel with file browser, search, tagging
- `styles.py` → All theme definitions and color constants
- `quick_look.py` → File preview window (images, text, Excel)

### Touch Points

| Purpose | File | Lines |
|---------|------|-------|
| Panel component | `folder_card.py` | `FolderCard` class |
| Theme colors | `styles.py` | `THEMES`, `ACCENT_COLORS` |
| File type colors | `styles.py` | `TYPE_COLORS` |
| Tag colors | `styles.py` | `TAG_COLORS` |
| Keyboard bindings | `folder_card.py` | 168-175 |
| File icons | `folder_card.py` | 34-52 |
| Analytics bar | `folder_card.py` | 282-324 |

---

## Quick Search Commands

```bash
# Find all CustomTkinter components
rg -n "class \w+\(ctk\." ui/

# Find button definitions
rg -n "CTkButton" ui/

# Find treeview operations
rg -n "self.tree\." ui/folder_card.py

# Find theme usage
rg -n "THEMES\[" ui/

# Find callback bindings
rg -n "\.bind\(" ui/

# Find after() scheduling (for thread safety)
rg -n "\.after\(" ui/
```

---

## Common Gotchas

1. **Thread Safety**: Use `self.after(ms, callback)` for UI updates from watchdog events
   - Example: `folder_card.py` line 266
   
2. **Treeview Styling**: Must use `ttk.Style()` - CustomTkinter doesn't style Treeview
   - Example: `folder_card.py` lines 212-214

3. **Focus Mode**: `toggle_focus_mode()` destroys and recreates `main_container`
   - All panel references are cleared and recreated
   
4. **Icon Garbage Collection**: Keep `icon_images` dict as instance variable

5. **Font Sizing**: Use `update_font_size()` method to update all fonts consistently
   - Example: `folder_card.py` lines 177-187

---

## Testing

No dedicated UI tests - test manually:

1. Run `python work_dashboard.py`
2. Test panel operations (browse, search, filter)
3. Test file operations (copy, paste, delete)
4. Test tagging (right-click → Tags & Notes)
5. Test theme switching (may require restart)
