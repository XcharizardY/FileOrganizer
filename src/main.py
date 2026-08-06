import sys
import os
import json
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QSystemTrayIcon, QMenu, QFileDialog, 
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QCheckBox,
    QScrollArea, QWidget, QLineEdit, QListWidget
)
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QThread, Qt

from background_watcher import BackgroundWatcher

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SRC_DIR)
CONFIG_PATH = os.path.join(PROJECT_ROOT, "config.json")
ICON_PATH = os.path.join(PROJECT_ROOT, "assets", "tray_icon.svg")

CATEGORIES_LIST = [
    "Images", "Documents", "Spreadsheets", "Presentations", 
    "Code", "Archives", "Videos", "Audio", "Executables", "Fonts", "Others"
]

class ScanResultsDialog(QDialog):
    def __init__(self, matches, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Scan Results")
        self.setFixedSize(550, 380)
        
        # Stripped out the broken QCheckBox::indicator overrides to restore native checkmarks
        self.setStyleSheet("""
            QDialog, QWidget#scrollWidget { background-color: #121212; color: #E0E0E0; }
            QLabel { font-size: 13px; color: #FFFFFF; font-weight: bold; }
            QPushButton { background-color: #7a0518; color: #FFFFFF; border: none; padding: 8px 14px; border-radius: 5px; font-weight: bold; }
            QPushButton:hover { background-color: #9c0b24; }
            QPushButton:pressed { background-color: #5c0210; }
            QPushButton#btnCancel { background-color: #333333; }
            QPushButton#btnCancel:hover { background-color: #444444; }
            QCheckBox { color: #E0E0E0; font-size: 14px; font-weight: bold; spacing: 8px; margin-bottom: 5px; }
            QScrollArea { border: 1px solid #2A2A2A; background-color: #121212; border-radius: 6px; }
        """)
        
        self.selected_results = {}
        self.checkboxes = {}
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel("Select the destinations to apply:")
        title.setStyleSheet("color: #FFCC00; font-size: 14px;")
        layout.addWidget(title)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_widget.setObjectName("scrollWidget")
        scroll_layout = QVBoxLayout(scroll_widget)
        
        for cat, path in matches.items():
            chk = QCheckBox(f"{cat}  ➔  {path}")
            chk.setChecked(True)
            self.checkboxes[cat] = (chk, path)
            scroll_layout.addWidget(chk)
            
        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        btn_layout = QHBoxLayout()
        btn_cancel = QPushButton("Cancel")
        btn_cancel.setObjectName("btnCancel")
        btn_cancel.clicked.connect(self.reject)
        
        btn_apply = QPushButton("Apply Selected")
        btn_apply.clicked.connect(self.apply_selections)
        
        btn_layout.addStretch()
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_apply)
        layout.addLayout(btn_layout)
        
    def apply_selections(self):
        self.selected_results = {cat: path for cat, (chk, path) in self.checkboxes.items() if chk.isChecked()}
        self.accept()

class SettingsWindow(QDialog):
    def __init__(self, watch_folders, use_chrono, routing_map, sort_ext, parent=None):
        super().__init__(parent)
        self.setWindowTitle("FileOrganizerStealth - Settings")
        
        self.setWindowIcon(QIcon(ICON_PATH)) 
        self.setFixedSize(620, 640)
        
        self.setStyleSheet("""
            QDialog, QWidget#scrollWidget { background-color: #121212; color: #E0E0E0; }
            QLabel { font-size: 13px; color: #FFFFFF; font-weight: bold; }
            QLineEdit, QListWidget { background-color: #1A1A1A; color: #FFF; border: 1px solid #333; border-radius: 5px; padding: 6px; }
            QLineEdit:focus, QListWidget:focus { border: 1px solid #7a0518; }
            QPushButton { background-color: #7a0518; color: #FFFFFF; border: none; padding: 8px 14px; border-radius: 5px; font-weight: bold; }
            QPushButton:hover { background-color: #9c0b24; }
            QPushButton:pressed { background-color: #5c0210; }
            QPushButton#scanBtn { background-color: #D69E00; color: #121212; margin-top: 5px; margin-bottom: 5px;}
            QPushButton#scanBtn:hover { background-color: #FFCC00; }
            QCheckBox { color: #E0E0E0; font-size: 13px; font-weight: bold; spacing: 8px; }
            QScrollArea { border: 1px solid #2A2A2A; background-color: #121212; border-radius: 6px; }
            QScrollBar:vertical { border: none; background: #121212; width: 10px; margin: 2px; }
            QScrollBar::handle:vertical { background: #333; min-height: 20px; border-radius: 4px; }
            QScrollBar::handle:vertical:hover { background: #555; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
        """)

        self.watch_folders = watch_folders
        self.use_chrono = use_chrono
        self.routing_map = routing_map or {}
        self.sort_ext = sort_ext
        self.path_inputs = {}

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        main_layout.addWidget(QLabel("Folders to Watch (e.g., Downloads, Desktop):"))
        watch_row = QHBoxLayout()
        self.list_widget = QListWidget()
        self.list_widget.setFixedHeight(70)
        self.list_widget.addItems(self.watch_folders)
        watch_row.addWidget(self.list_widget)

        btn_layout = QVBoxLayout()
        btn_add = QPushButton("Add")
        btn_add.clicked.connect(self.add_watch_folder)
        btn_rem = QPushButton("Remove")
        btn_rem.clicked.connect(self.remove_watch_folder)
        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_rem)
        watch_row.addLayout(btn_layout)
        main_layout.addLayout(watch_row)

        self.chk_ext = QCheckBox("Organize into exact File Type folders (e.g., PDF, DOCX, ZIP)")
        self.chk_ext.setChecked(self.sort_ext)
        main_layout.addWidget(self.chk_ext)

        self.chk_chrono = QCheckBox("Enable Chronological Sub-folders (Year/Month)")
        self.chk_chrono.setChecked(self.use_chrono)
        main_layout.addWidget(self.chk_chrono)

        self.btn_scan = QPushButton("Smart Scan System for Existing Destinations")
        self.btn_scan.setObjectName("scanBtn")
        self.btn_scan.clicked.connect(self.run_smart_scan)
        main_layout.addWidget(self.btn_scan)

        routing_label = QLabel("Custom Destinations (Leave blank to sort locally):")
        routing_label.setStyleSheet("color: #FFCC00; margin-top: 5px;")
        main_layout.addWidget(routing_label)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_widget.setObjectName("scrollWidget")
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(12)

        for cat in CATEGORIES_LIST:
            row = QHBoxLayout()
            lbl = QLabel(cat)
            lbl.setFixedWidth(110)
            
            txt = QLineEdit()
            txt.setText(self.routing_map.get(cat, ""))
            txt.setPlaceholderText("Default")
            self.path_inputs[cat] = txt
            
            btn = QPushButton("Browse")
            btn.setFixedWidth(85)
            btn.clicked.connect(lambda checked, c=cat, t=txt: self.browse_category(c, t))
            
            row.addWidget(lbl)
            row.addWidget(txt)
            row.addWidget(btn)
            scroll_layout.addLayout(row)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll)

        self.btn_save = QPushButton("Save & Apply")
        self.btn_save.setFixedHeight(45)
        self.btn_save.clicked.connect(self.save_and_close)
        main_layout.addWidget(self.btn_save)

    def add_watch_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder to Watch")
        if folder and folder not in [self.list_widget.item(i).text() for i in range(self.list_widget.count())]:
            self.list_widget.addItem(folder)

    def remove_watch_folder(self):
        for item in self.list_widget.selectedItems():
            self.list_widget.takeItem(self.list_widget.row(item))

    def run_smart_scan(self):
        home = Path.home()
        
        # Added Archives to the scanner so it actually picks up your ZIP folder
        scan_targets = {
            "Documents": [home / "OneDrive" / "Documents", home / "Documents"],
            "Images": [home / "OneDrive" / "Pictures", home / "Pictures"],
            "Videos": [home / "OneDrive" / "Videos", home / "Videos"],
            "Audio": [home / "OneDrive" / "Music", home / "Music"],
            "Code": [home / "OneDrive" / "Documents" / "VS code", home / "Documents" / "VS code"],
            "Spreadsheets": [home / "OneDrive" / "Documents", home / "Documents"],
            "Presentations": [home / "OneDrive" / "Documents", home / "Documents"],
            "Archives": [home / "OneDrive" / "Documents", home / "Documents"]
        }
        
        found_matches = {}
        for cat, paths in scan_targets.items():
            for p in paths:
                if p.exists() and not self.path_inputs[cat].text():
                    if cat not in found_matches:
                        found_matches[cat] = str(p)
                    break 

        if found_matches:
            dialog = ScanResultsDialog(found_matches, self)
            if dialog.exec():
                selected = dialog.selected_results
                if selected:
                    for cat, path in selected.items():
                        self.path_inputs[cat].setText(path)
                    
                    self.chk_ext.setChecked(True)
                    self.btn_scan.setText("Scan Complete: Destinations Applied")
                    self.btn_scan.setStyleSheet("background-color: #2e7d32; color: white;")
                else:
                    self.btn_scan.setText("Scan Complete: No changes applied.")
        else:
            self.btn_scan.setText("Scan Complete: No standard folders found.")

    def browse_category(self, category, line_edit):
        folder = QFileDialog.getExistingDirectory(self, f"Select Destination for {category}")
        if folder:
            line_edit.setText(folder)

    def save_and_close(self):
        self.watch_folders = [self.list_widget.item(i).text() for i in range(self.list_widget.count())]
        
        for cat, txt in self.path_inputs.items():
            val = txt.text().strip()
            if val:
                self.routing_map[cat] = val
            elif cat in self.routing_map:
                del self.routing_map[cat]
                
        self.use_chrono = self.chk_chrono.isChecked()
        self.sort_ext = self.chk_ext.isChecked()
        self.accept()

class WatcherThread(QThread):
    def __init__(self, watch_folders, use_chronological, routing_map, sort_by_extension):
        super().__init__()
        self.watch_folders = watch_folders
        self.use_chronological = use_chronological
        self.routing_map = routing_map
        self.sort_by_extension = sort_by_extension
        self.watcher = BackgroundWatcher(self.watch_folders, self.use_chronological, self.routing_map, self.sort_by_extension)

    def run(self):
        self.watcher.start_watching()

    def stop(self):
        self.watcher.stop()
        self.quit()
        self.wait()

class StealthOrganizer:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        
        self.app.setWindowIcon(QIcon(ICON_PATH))
        
        self.thread = None
        self.watch_folders, self.use_chronological, self.routing_map, self.sort_by_extension = self.load_config()
        
        self.init_tray()
        
        if self.watch_folders:
            self.start_watching()
        else:
            self.open_settings()

    def load_config(self):
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r") as f:
                    data = json.load(f)
                    
                    watch_folders = data.get("watch_folders", [])
                    if not watch_folders and data.get("target_folder"):
                        watch_folders = [data.get("target_folder")]
                        
                    return (
                        watch_folders, 
                        data.get("use_chronological", True), 
                        data.get("routing_map", {}),
                        data.get("sort_by_extension", False)
                    )
            except Exception:
                pass
        return [], True, {}, False

    def save_config(self, folders, chrono, routing_map, sort_ext):
        with open(CONFIG_PATH, "w") as f:
            json.dump({
                "watch_folders": folders, 
                "use_chronological": chrono,
                "routing_map": routing_map,
                "sort_by_extension": sort_ext
            }, f, indent=4)

    def init_tray(self):
        self.tray = QSystemTrayIcon()
        if os.path.exists(ICON_PATH):
            self.tray.setIcon(QIcon(ICON_PATH))
            
        self.menu = QMenu()
        self.settings_action = QAction("Settings")
        self.settings_action.triggered.connect(self.open_settings)
        self.menu.addAction(self.settings_action)
        self.menu.addSeparator()
        self.quit_action = QAction("Quit Organizer")
        self.quit_action.triggered.connect(self.quit_app)
        self.menu.addAction(self.quit_action)

        self.tray.setContextMenu(self.menu)
        
        status = f"Watching {len(self.watch_folders)} folder(s)" if self.watch_folders else "FileOrganizerStealth (Idle)"
        self.tray.setToolTip(f"FileOrganizerStealth Active\n{status}")
        self.tray.show()

    def open_settings(self):
        dialog = SettingsWindow(self.watch_folders, self.use_chronological, self.routing_map, self.sort_by_extension)
        if dialog.exec(): 
            self.watch_folders = dialog.watch_folders
            self.use_chronological = dialog.use_chrono
            self.routing_map = dialog.routing_map
            self.sort_by_extension = dialog.sort_ext
            
            self.save_config(self.watch_folders, self.use_chronological, self.routing_map, self.sort_by_extension)
            
            if self.watch_folders:
                self.tray.setToolTip(f"FileOrganizerStealth Active\nWatching {len(self.watch_folders)} folder(s)")
                self.start_watching()

    def start_watching(self):
        if self.thread and self.thread.isRunning():
            self.thread.stop()
            
        if self.watch_folders:
            self.thread = WatcherThread(self.watch_folders, self.use_chronological, self.routing_map, self.sort_by_extension)
            self.thread.start()
            self.tray.showMessage("FileOrganizerStealth Active", f"Silently organizing {len(self.watch_folders)} folder(s)", QSystemTrayIcon.MessageIcon.Information, 2000)

    def quit_app(self):
        if self.thread and self.thread.isRunning():
            self.thread.stop()
        self.tray.hide()
        self.app.quit()

if __name__ == "__main__":
    organizer = StealthOrganizer()
    sys.exit(organizer.app.exec())