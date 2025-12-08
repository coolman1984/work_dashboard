import json
import os

TAGS_FILE = "file_tags.json"

class MetadataService:
    _tags = {}

    @classmethod
    def load_tags(cls):
        if os.path.exists(TAGS_FILE):
            try:
                with open(TAGS_FILE, 'r') as f:
                    cls._tags = json.load(f)
            except (json.JSONDecodeError, OSError) as e:
                print(f"Error loading tags: {e}")
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
        if note is not None: # Allow empty string to clear note if needed, though usually we might want remove_tag for that
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

    @classmethod
    def remove_color(cls, path):
        if path in cls._tags and "color" in cls._tags[path]:
            del cls._tags[path]["color"]
            # If entry is empty, remove it entirely
            if not cls._tags[path]:
                del cls._tags[path]
            cls.save_tags()
