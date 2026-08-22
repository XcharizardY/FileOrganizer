import time
import threading
from pathlib import Path
from ai_sorter import sort_folder
from logger_setup import get_logger

logger = get_logger()

try:
    from dashboard_bridge import DashboardBridge
except ImportError:
    DashboardBridge = None


class BackgroundWatcher:
    def __init__(self, watch_folders, use_chronological=True, routing_map=None,
                 sort_by_extension=False, dashboard_db_path=None, on_file_organized=None):
        self.watch_folders = watch_folders if isinstance(watch_folders, list) else []
        self.use_chronological = use_chronological
        self.routing_map = routing_map or {}
        self.sort_by_extension = sort_by_extension
        # Callback(msg: str) - called from THIS background thread, so the
        # receiver (main.py) must marshal it back to the GUI thread, e.g.
        # via a pyqtSignal. Never touch QSystemTrayIcon directly from here.
        self.on_file_organized = on_file_organized
        self._stop_event = threading.Event()

        self.bridge = None
        if dashboard_db_path and DashboardBridge:
            try:
                self.bridge = DashboardBridge(dashboard_db_path)
            except Exception as e:
                logger.warning(f"Dashboard bridge disabled: {e}")

    def start_watching(self):
        self._stop_event.clear()
        logger.info(f"Watcher started - watching {len(self.watch_folders)} folder(s): {self.watch_folders}")

        while not self._stop_event.is_set():
            for folder in self.watch_folders:
                if folder and Path(folder).exists():
                    try:
                        active_projects = self.bridge.get_active_projects() if self.bridge else []
                        moved_files = sort_folder(
                            folder,
                            self.use_chronological,
                            self.routing_map,
                            self.sort_by_extension,
                            active_projects,
                        )

                        for file_data in moved_files:
                            logger.info(f"Moved '{file_data['filename']}' -> {file_data['dest_path']}")

                            if self.bridge:
                                self.bridge.log_document(
                                    project_id=file_data["project_id"],
                                    client_id=file_data["client_id"],
                                    file_name=file_data["filename"],
                                    dest_path=file_data["dest_path"],
                                    category=file_data["doc_category"],
                                    file_type=file_data["file_type"],
                                )

                            if self.on_file_organized:
                                label = file_data["project_name"] or "General"
                                msg = f"{file_data['filename']} → {label}"
                                self.on_file_organized(msg)
                    except Exception as e:
                        logger.error(f"Engine crash in '{folder}': {e}")

            for _ in range(5):
                if self._stop_event.is_set():
                    break
                time.sleep(1)

    def stop(self):
        logger.info("Watcher stopped")
        self._stop_event.set()
