def get_app_data_dir():
    """Get consistent app data directory across platforms."""
    if os.name == 'nt':
        base = os.environ.get('APPDATA', os.path.expanduser('~'))
    else:
        base = os.path.expanduser('~/.config')
    
    app_dir = os.path.join(base, 'WorkDashboard')
    os.makedirs(app_dir, exist_ok=True)
    return app_dir

CONFIG_FILE = os.path.join(get_app_data_dir(), "dashboard_config.json")

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
