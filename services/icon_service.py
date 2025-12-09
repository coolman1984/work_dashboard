import os
import tkinter as tk

class IconService:
    """Singleton icon cache to prevent reloading images for every panel."""
    _icons = {}
    _loaded = False

    @classmethod
    def get_icon(cls, name: str) -> tk.PhotoImage:
        """Get a cached icon by name."""
        if not cls._loaded:
            try:
                cls._load_all_icons()
            except tk.TclError as e:
                print(f"Warning: Could not load icons (Tkinter not ready): {e}")
                cls._loaded = True  # Prevent repeated attempts
        return cls._icons.get(name)

    @classmethod
    def get_file_icon(cls, filename: str, is_folder: bool = False) -> tk.PhotoImage:
        """Get appropriate icon for a file or folder."""
        if is_folder:
            return cls.get_icon('folder')

        ext = os.path.splitext(filename)[1].lower()
        icon_map = {
            '.pdf': 'document', '.docx': 'document', '.doc': 'document',
            '.txt': 'document', '.md': 'document',
            '.xlsx': 'spreadsheet', '.xls': 'spreadsheet', '.csv': 'spreadsheet',
            '.jpg': 'image', '.jpeg': 'image', '.png': 'image',
            '.gif': 'image', '.bmp': 'image',
            '.py': 'code', '.js': 'code', '.html': 'code',
            '.css': 'code', '.json': 'code',
            '.zip': 'archive', '.rar': 'archive', '.7z': 'archive',
            '.exe': 'executable', '.msi': 'executable',
            '.mp3': 'audio', '.wav': 'audio',
            '.mp4': 'video', '.avi': 'video',
        }
        icon_name = icon_map.get(ext, 'default')
        return cls.get_icon(icon_name)

    @classmethod
    def _load_all_icons(cls):
        """Load all icons into memory once."""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        icon_dir = os.path.join(base_dir, 'icons')
        
        icon_paths = {
            'folder': 'folder.png',
            'document': 'document.png',
            'spreadsheet': 'spreadsheet.png',
            'image': 'image.png',
            'code': 'code.png',
            'archive': 'archive.png',
            'executable': 'executable.png',
            'audio': 'audio.png',
            'video': 'video.png',
            'default': 'file.png'
        }

        for name, filename in icon_paths.items():
            path = os.path.join(icon_dir, filename)
            if os.path.exists(path):
                try:
                    cls._icons[name] = tk.PhotoImage(file=path)
                except Exception as e:
                    print(f"Warning: Failed to load icon {name}: {e}")
                    cls._icons[name] = None
            else:
                # print(f"Warning: Icon file not found: {path}")
                cls._icons[name] = None
        
        cls._loaded = True
