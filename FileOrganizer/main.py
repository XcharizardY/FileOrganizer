import sys
import os
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QFileDialog, QLabel, QTextEdit, QLineEdit,
    QHBoxLayout, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QIcon

from background_watcher import BackgroundWatcher
from search_engine import SearchEngine
from analytics import Analytics


# ---------------------------
# Paths
# ---------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ICONS_DIR = os.path.join(BASE_DIR, "icons")


# ---------------------------
# Background Thread
# ---------------------------
class WatcherThread(QThread):
    status_signal = pyqtSignal(str)

    def __init__(self, folder):
        super().__init__()
        self.folder = folder

    def run(self):
        watcher = BackgroundWatcher(self.folder)

        def emit_message(msg):
            self.status_signal.emit(msg)

        watcher.start_watching(emit_message)


# ---------------------------
# Main UI
# ---------------------------
class SmartOrganizer(QWidget):
    def __init__(self):
        super().__init__()

        self.search_engine = SearchEngine()
        self.folder = None
        self.watcher_thread = None

        self.setWindowTitle("AI Smart File Organizer")
        self.setMinimumSize(900, 650)

        self.setStyleSheet("""
        /* ================== BASE ================== */
        QWidget {
            background-color: #0a0a0a;
            color: #E0E0E0;
            font-size: 14px;
        }

        /* ================== LABELS ================== */
        QLabel {
            color: #550000;
            font-weight: 600;
        }

        /* ================== BUTTONS ================== */
        QPushButton {
            background-color: #550000;
            color: #FFFFFF;
            border: none;
            padding: 10px;
            border-radius: 8px;
            font-weight: 600;
        }

        QPushButton:hover {
            background-color: #770000;
        }

        QPushButton:pressed {
            background-color: #3a0000;
        }

        /* ================== INPUTS ================== */
        QLineEdit, QTextEdit {
            background-color: #141414;
            border: 2px solid #222222;
            border-radius: 8px;
            padding: 8px;
            color: #FFFFFF;
        }

        QLineEdit:focus, QTextEdit:focus {
            border: 2px solid #550000;
        }

        /* ================== LIST ================== */
        QListWidget {
            background-color: #121212;
            border: 2px solid #222222;
            border-radius: 10px;
            padding: 6px;
            outline: none;
        }

        QListWidget::item {
            padding: 10px;
            margin: 4px;
            border-radius: 6px;
            color: #E0E0E0;
        }

        QListWidget::item:hover {
            background-color: #1a1a1a;
        }

        QListWidget::item:selected {
            background-color: #550000;
            color: #FFFFFF;
        }

        /* ================== SCROLLBAR ================== */
        QScrollBar:vertical {
            background: transparent;
            width: 12px;
        }

        QScrollBar::handle:vertical {
            background: #2a2a2a;
            border-radius: 6px;
        }

        QScrollBar::handle:vertical:hover {
            background: #550000;
        }

        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {
            height: 0px;
        }
        """)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)

        # Header
        self.label = QLabel("No folder selected")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.label)

        # Buttons Row
        button_row = QHBoxLayout()

        select_btn = QPushButton("Select Folder")
        select_btn.clicked.connect(self.select_folder)

        watch_btn = QPushButton("Start Organizer")
        watch_btn.clicked.connect(self.start_background)

        stats_btn = QPushButton("Analytics")
        stats_btn.clicked.connect(self.show_stats)

        button_row.addWidget(select_btn)
        button_row.addWidget(watch_btn)
        button_row.addWidget(stats_btn)

        main_layout.addLayout(button_row)

        # Search Row
        search_row = QHBoxLayout()

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search files...")

        search_btn = QPushButton("Search")
        self.search_box.textChanged.connect(self.search)

        search_row.addWidget(self.search_box)
        search_row.addWidget(search_btn)

        main_layout.addLayout(search_row)

        # File List
        self.file_list = QListWidget()
        main_layout.addWidget(self.file_list)

        # Output area
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        main_layout.addWidget(self.output)

        self.setLayout(main_layout)

    # ---------------------------
    # ICON HANDLER (NEW)
    # ---------------------------
    def get_icon_for_file(self, filename: str) -> QIcon:
        ext = os.path.splitext(filename)[1].lower()

        icon_map = {

            # ================= Images =================
            ".jpg": "image.svg",
            ".jpeg": "image.svg",
            ".png": "image.svg",
            ".gif": "image.svg",
            ".bmp": "image.svg",
            ".webp": "image.svg",
            ".svg": "image.svg",
            ".heic": "image.svg",
            ".tiff": "image.svg",

            # ================= Documents =================
            ".pdf": "document.svg",
            ".doc": "document.svg",
            ".docx": "document.svg",
            ".txt": "document.svg",
            ".rtf": "document.svg",
            ".odt": "document.svg",

            # ================= Spreadsheets =================
            ".xls": "spreadsheet.svg",
            ".xlsx": "spreadsheet.svg",
            ".csv": "spreadsheet.svg",
            ".ods": "spreadsheet.svg",

            # ================= Presentations =================
            ".ppt": "presentation.svg",
            ".pptx": "presentation.svg",
            ".odp": "presentation.svg",

            # ================= Code =================
            ".py": "code.svg",
            ".js": "code.svg",
            ".ts": "code.svg",
            ".html": "code.svg",
            ".css": "code.svg",
            ".cpp": "code.svg",
            ".c": "code.svg",
            ".java": "code.svg",
            ".json": "code.svg",
            ".xml": "code.svg",
            ".yaml": "code.svg",
            ".yml": "code.svg",
            ".sql": "code.svg",

            # ================= Archives =================
            ".zip": "archive.svg",
            ".rar": "archive.svg",
            ".7z": "archive.svg",
            ".tar": "archive.svg",
            ".gz": "archive.svg",

            # ================= Videos =================
            ".mp4": "video.svg",
            ".mkv": "video.svg",
            ".avi": "video.svg",
            ".mov": "video.svg",
            ".wmv": "video.svg",
            ".flv": "video.svg",

            # ================= Audio =================
            ".mp3": "audio.svg",
            ".wav": "audio.svg",
            ".aac": "audio.svg",
            ".flac": "audio.svg",
            ".ogg": "audio.svg",
            ".m4a": "audio.svg",

            # ================= Executables =================
            ".exe": "exe.svg",
            ".msi": "exe.svg",
            ".apk": "exe.svg",
            ".bat": "exe.svg",

            # ================= Fonts =================
            ".ttf": "font.svg",
            ".otf": "font.svg",
        }

        icon_name = icon_map.get(ext, "file.svg")
        return QIcon(os.path.join(ICONS_DIR, icon_name))

    # ---------------------------
    # Load Folder Files
    # ---------------------------
    def load_files(self):
        self.file_list.clear()

        if not self.folder:
            return

        for entry in os.listdir(self.folder):
            icon = self.get_icon_for_file(entry)
            item = QListWidgetItem(icon, entry)
            self.file_list.addItem(item)

    # ---------------------------
    # Select Folder
    # ---------------------------
    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.folder = folder
            self.label.setText(folder)

            self.search_engine.index_folder(folder)
            self.load_files()

    # ---------------------------
    # Start Background Organizer
    # ---------------------------
    def start_background(self):
        if not self.folder:
            self.output.setText("Please select a folder first.")
            return

        self.watcher_thread = WatcherThread(self.folder)
        self.watcher_thread.status_signal.connect(self.output.append)
        self.watcher_thread.start()

    # ---------------------------
    # Search Files
    # ---------------------------
    def search(self):
        if not self.folder:
            return

        query = self.search_box.text().strip()
        self.file_list.clear()

        if not query:
            self.load_files()
            return

        results = self.search_engine.search(query)

        if results:
            for path in results:
                name = os.path.basename(path)
                icon = self.get_icon_for_file(name)
                self.file_list.addItem(QListWidgetItem(icon, name))

            self.output.setText(f"Found {len(results)} result(s).")
        else:
            self.output.setText("No results found.")

    # ---------------------------
    # Analytics
    # ---------------------------

    def show_stats(self):
        if not self.folder:
            self.output.setText("Please select a folder first.")
            return

        self.file_list.clear()

        total_files = 0
        total_size = 0

        for root, _, files in os.walk(self.folder):
            for file in files:
                full_path = os.path.join(root, file)

                try:
                    size = os.path.getsize(full_path)
                except:
                    continue

                total_files += 1
                total_size += size

                icon = self.get_icon_for_file(file)
                size_kb = round(size / 1024, 2)

                item = QListWidgetItem(
                    icon, f"{file}  ({size_kb} KB)"
                )
                self.file_list.addItem(item)

        total_size_mb = round(total_size / (1024 * 1024), 2)

        self.output.setText(
            f"Total Files: {total_files}\n"
            f"Total Size: {total_size_mb} MB"
        )


# ---------------------------
# App Entry
# ---------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SmartOrganizer()
    window.show()
    sys.exit(app.exec())
