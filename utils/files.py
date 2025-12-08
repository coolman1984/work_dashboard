import os
import datetime
from tkinter import messagebox

def open_path(path):
    try: os.startfile(path)
    except OSError as e: messagebox.showerror("Error", f"Could not open path:\n{e}")

def get_file_info(filepath):
    try:
        stats = os.stat(filepath)
        size_mb = stats.st_size / (1024 * 1024)
        mod_time = datetime.datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M')
        return stats.st_size, size_mb, mod_time
    except OSError:
        return 0, 0.0, "Unknown"
