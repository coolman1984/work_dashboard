import os
import json

CONFIG_FILE = "dashboard_config.json"

class ConfigManager:
    @staticmethod
    def load_config():
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f: return json.load(f)
            except (json.JSONDecodeError, OSError) as e:
                print(f"Error loading config: {e}")
                return {"workspaces": {}}
        return {"workspaces": {}}

    @staticmethod
    def save_config(data):
        try:
            with open(CONFIG_FILE, 'w') as f: json.dump(data, f)
        except Exception as e: print(f"Error saving config: {e}")
