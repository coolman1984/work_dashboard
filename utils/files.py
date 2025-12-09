import os
import datetime
from tkinter import messagebox

import platform
import subprocess

def open_path(path):
    try:
        system = platform.system()
        if system == 'Windows':
            os.startfile(path)
        elif system == 'Darwin':  # macOS
            subprocess.run(['open', path], check=True)
        else:  # Linux
            subprocess.run(['xdg-open', path], check=True)
    except (OSError, subprocess.CalledProcessError) as e:
        messagebox.showerror("Error", f"Could not open path:\n{e}")

def get_file_info(filepath):
    try:
        stats = os.stat(filepath)
        size_mb = stats.st_size / (1024 * 1024)
        mod_time = datetime.datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M')
        return stats.st_size, size_mb, mod_time
    except OSError:
        return 0, 0.0, "Unknown"

