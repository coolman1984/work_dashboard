# Standalone Tagged Files App - Implementation Plan

## Overview
Create a standalone file tagging application based on the Tagged Files dialog.

---

## Project Structure

```
Tagged Files/
├── main.py                      # Entry point
├── requirements.txt             # Dependencies
├── README.md                    # Documentation
├── file_tags.json              # Tag storage (created automatically)
│
├── ui/
│   ├── __init__.py
│   ├── main_window.py          # Main application window
│   ├── tagged_files_dialog.py  # File list dialog (from work_dashboard)
│   └── styles.py               # Theme definitions
│
├── services/
│   ├── __init__.py
│   └── metadata_service.py     # Tag management service
│
└── utils/
    ├── __init__.py
    └── files.py                # File utilities
```

---

## Files to Create

### 1. main.py
```python
import customtkinter as ctk
from ui.main_window import MainWindow

def main():
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    
    app = MainWindow()
    app.mainloop()

if __name__ == "__main__":
    main()
```

### 2. requirements.txt
```
customtkinter>=5.2.0
```

### 3. ui/__init__.py
```python
# UI Package
```

### 4. ui/styles.py
```python
THEMES = {
    "Light": {
        "bg": "#F5F5F5",
        "card": "#FFFFFF",
        "text": "#333333",
        "subtext": "#888888",
        "hover": "#E8E8E8",
        "border": "#DDDDDD"
    },
    "Dark": {
        "bg": "#1E1E1E",
        "card": "#2D2D2D",
        "text": "#FFFFFF",
        "subtext": "#888888",
        "hover": "#3D3D3D",
        "border": "#444444"
    }
}

TAG_COLORS = {
    "red": "#F44336",
    "green": "#4CAF50",
    "yellow": "#FFC107"
}
```

### 5. services/__init__.py
```python
# Services Package
```

### 6. services/metadata_service.py
```python
import os
import json

TAGS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "file_tags.json")

class MetadataService:
    _tags = {}

    @classmethod
    def load_tags(cls):
        if os.path.exists(TAGS_FILE):
            try:
                with open(TAGS_FILE, 'r') as f:
                    cls._tags = json.load(f)
            except (json.JSONDecodeError, OSError):
                cls._tags = {}
        else:
            cls._tags = {}

    @classmethod
    def save_tags(cls):
        try:
            with open(TAGS_FILE, 'w') as f:
                json.dump(cls._tags, f, indent=4)
        except Exception as e:
            print(f"Error saving tags: {e}")

    @classmethod
    def set_tag(cls, path, color=None, note=None):
        if path not in cls._tags:
            cls._tags[path] = {}
        if color:
            cls._tags[path]["color"] = color
        if note is not None:
            cls._tags[path]["note"] = note
        cls.save_tags()

    @classmethod
    def get_tag(cls, path):
        return cls._tags.get(path, {})

    @classmethod
    def get_all_tags(cls):
        return cls._tags

    @classmethod
    def remove_tag(cls, path):
        if path in cls._tags:
            del cls._tags[path]
            cls.save_tags()
```

### 7. utils/__init__.py
```python
# Utils Package
```

### 8. utils/files.py
```python
import os
import subprocess
import sys

def open_path(path):
    """Open a file or folder with the default application."""
    if sys.platform == 'win32':
        os.startfile(path)
    elif sys.platform == 'darwin':
        subprocess.run(['open', path])
    else:
        subprocess.run(['xdg-open', path])

def get_file_info(path):
    """Get file size and modification time."""
    try:
        stat = os.stat(path)
        return {
            'size': stat.st_size,
            'mtime': stat.st_mtime
        }
    except OSError:
        return {'size': 0, 'mtime': 0}
```

### 9. ui/main_window.py
```python
import customtkinter as ctk
from ui.tagged_files_dialog import TaggedFilesDialog
from ui.styles import THEMES

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Tagged Files")
        self.theme = THEMES["Light"]
        
        # Position on left side of screen
        screen_height = self.winfo_screenheight()
        self.geometry(f"550x{screen_height - 80}+0+0")
        
        # Create the tagged files content
        self._create_content()
    
    def _create_content(self):
        # Embed TaggedFilesDialog content directly
        dialog = TaggedFilesDialog(self, "Light", 14)
        dialog.pack(fill="both", expand=True)
```

### 10. ui/tagged_files_dialog.py
Copy the full content from:
`c:\Users\m.labib\Documents\GitHub\work_dashboard\ui\tagged_files_dialog.py`

**Important**: Change the imports at the top:
```python
from services.metadata_service import MetadataService
from utils.files import open_path, get_file_info
from ui.styles import THEMES, TAG_COLORS
```

---

## Setup Steps

1. Create the folder structure above
2. Copy each file content
3. Open terminal in the folder
4. Run: `python -m venv .venv`
5. Run: `.venv\Scripts\activate`
6. Run: `pip install customtkinter`
7. Run: `python main.py`

---

## Build Executable

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "TaggedFiles" main.py
```

The .exe will be in the `dist` folder.
