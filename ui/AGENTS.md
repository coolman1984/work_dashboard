# AGENTS.md - UI Layer

## Package Identity

- **Purpose**: GUI components for the Work Dashboard application
- **Framework**: CustomTkinter (modern Tkinter wrapper) + ttk for Treeviews
- **Main class**: `FolderCard` - the multi-panel file browser component

---

## Key Files

| File | Purpose | Lines |
|------|---------|-------|
| `folder_card.py` | Main panel component with file browser | ~650 |
| `dashboard.py` | Main application window (alternative entry) | ~450 |
| `quick_look.py` | File preview popup window | ~60 |
| `styles.py` | Theme definitions and color constants | ~30 |

---

## Patterns & Conventions

### Component Structure
- ✅ **DO**: Inherit from `ctk.CTkFrame` or `ctk.CTkToplevel`
- ✅ **DO**: Use `grid()` layout with `weight` for responsive sizing
- ❌ **DON'T**: Mix `grid()` and `pack()` in the same container

### File Organization
```
ui/
├── __init__.py          # Empty, for package imports
├── folder_card.py       # Primary file browser panel
├── dashboard.py         # Main window (backup implementation)
├── quick_look.py        # File preview window
└── styles.py            # All colors/themes defined here
```

### Theming Pattern
```python
# ✅ Always use theme dict from styles.py
from ui.styles import THEMES, ACCENT_COLORS
t = THEMES[self.current_theme]
self.configure(fg_color=t["card"])

# ❌ Never hardcode colors
self.configure(fg_color="#2c2c2c")  # BAD
```

### Treeview with Tags
```python
# ✅ Example from folder_card.py lines 216-221
for name, color in TAG_COLORS.items():
    self.tree.tag_configure(name, foreground="#000000", background=color, font=normal_font)
```

---

## Touch Points

- **Main panel component**: `folder_card.py` → `FolderCard` class
- **Theme colors**: `styles.py` → `THEMES`, `ACCENT_COLORS`, `TYPE_COLORS`
- **File icons**: Located in `../icons/*.png`, loaded in `folder_card.py` lines 34-52
- **Keyboard bindings**: `folder_card.py` lines 168-175

---

## JIT Index Hints

```bash
# Find all CTk components
rg -n "class \w+\(ctk\." ui/

# Find button definitions
rg -n "CTkButton" ui/

# Find treeview operations
rg -n "self.tree\." ui/folder_card.py

# Find theme usage
rg -n "THEMES\[" ui/

# Find callback registrations
rg -n "\.bind\(" ui/
```

---

## Common Gotchas

1. **Thread safety**: Use `self.after(ms, callback)` for UI updates from watchdog
2. **Treeview styling**: Must use `ttk.Style()` for Treeview, not CTk methods
3. **Focus mode**: Destroys and recreates `main_container` - see `toggle_focus_mode()`
4. **Icon references**: Keep `icon_images` dict alive or images garbage collect

---

## Pre-PR Checks

```bash
python -c "from ui.folder_card import FolderCard; from ui.styles import THEMES; print('UI imports OK')"
```
