import time
import threading
from pathlib import Path
from ai_sorter import sort_folder

class BackgroundWatcher:
    def __init__(self, watch_folders, use_chronological=True, routing_map=None, sort_by_extension=False):
        self.watch_folders = watch_folders if isinstance(watch_folders, list) else []
        self.use_chronological = use_chronological
        self.routing_map = routing_map or {}
        self.sort_by_extension = sort_by_extension
        self._stop_event = threading.Event()

    def start_watching(self):
        self._stop_event.clear()
        
        while not self._stop_event.is_set():
            for folder in self.watch_folders:
                if folder and Path(folder).exists():
                    try:
                        sort_folder(folder, self.use_chronological, self.routing_map, self.sort_by_extension)
                    except Exception as e:
                        print(f"Engine crash in {folder}: {e}")
            
            for _ in range(5):
                if self._stop_event.is_set():
                    break
                time.sleep(1)

    def stop(self):
        self._stop_event.set()