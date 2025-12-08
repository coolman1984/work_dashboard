import time
from watchdog.events import FileSystemEventHandler

class FolderChangeHandler(FileSystemEventHandler):
    def __init__(self, callback): self.callback = callback; self.last_refresh = 0
    def on_any_event(self, event):
        if time.time() - self.last_refresh > 1.0: self.callback(); self.last_refresh = time.time()
