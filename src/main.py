import sys
import os
import json
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QSystemTrayIcon, QMenu, QFileDialog, 
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QCheckBox,
    QScrollArea, QWidget, QLineEdit, QListWidget, QFrame, QMessageBox
)
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QThread, Qt, pyqtSignal

from background_watcher import BackgroundWatcher
import startup_manager
from logger_setup import get_logger, LOG_PATH

logger = get_logger()

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SRC_DIR)
CONFIG_PATH = os.path.join(PROJECT_ROOT, "config.json")
ICON_PATH = os.path.join(PROJECT_ROOT, "assets", "tray_icon.svg")
MAIN_PY_PATH = os.path.join(SRC_DIR, "main.py")

CATEGORIES_LIST = [
    "Images", "Documents", "Spreadsheets", "Presentations", 
    "Code", "Archives", "Videos", "Audio", "Executables", "Fonts", "Others"
]

class ScanResultsDialog(QDialog):
    def __init__(self, matches, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Scan Results")
        self.setFixedSize(560, 400)
        
        self.setStyleSheet("""
            QDialog { background-color: #0b0b0d; }
            QWidget#scrollWidget { background-color: transparent; }
            QLabel#dialogHeader { color: #FFFFFF; font-size: 16px; font-weight: 800; }
            QLabel#dialogSubheader { color: #86868c; font-size: 12px; font-weight: 400; }
            QFrame#card { background-color: #16161a; border: 1px solid #26262b; border-radius: 8px; }
            QCheckBox { color: #e5e5e8; font-size: 13px; font-weight: 600; spacing: 10px; padding: 10px 4px; }
            QCheckBox#matchPath { color: #86868c; font-size: 11px; font-weight: 400; margin-left: 28px; margin-top: -6px; }
            QPushButton { background-color: #7a0518; color: #FFFFFF; border: none; padding: 9px 16px; border-radius: 6px; font-weight: 600; font-size: 12px; }
            QPushButton:hover { background-color: #9c0b24; }
            QPushButton:pressed { background-color: #5c0210; }
            QPushButton#btnCancel { background-color: #232328; color: #e5e5e8; }
            QPushButton#btnCancel:hover { background-color: #2d2d33; }
            QScrollArea { border: none; background-color: transparent; }
            QScrollBar:vertical { border: none; background: transparent; width: 8px; margin: 0; }
            QScrollBar::handle:vertical { background: #333338; min-height: 24px; border-radius: 4px; }
            QScrollBar::handle:vertical:hover { background: #48484f; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
        """)
        
        self.selected_results = {}
        self.checkboxes = {}
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(12)
        
        title = QLabel("Destinations Found")
        title.setObjectName("dialogHeader")
        subtitle = QLabel("Uncheck any you don't want to apply.")
        subtitle.setObjectName("dialogSubheader")
        layout.addWidget(title)
        layout.addWidget(subtitle)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        card = QFrame()
        card.setObjectName("card")
        scroll_layout = QVBoxLayout(card)
        scroll_layout.setContentsMargins(14, 10, 14, 10)
        scroll_layout.setSpacing(0)
        
        for i, (cat, path) in enumerate(matches.items()):
            if i > 0:
                divider = QFrame()
                divider.setFixedHeight(1)
                divider.setStyleSheet("background-color: #232328; border: none;")
                scroll_layout.addWidget(divider)
            chk = QCheckBox(cat)
            chk.setChecked(True)
            path_lbl = QLabel(path)
            path_lbl.setObjectName("matchPath")
            self.checkboxes[cat] = (chk, path)
            scroll_layout.addWidget(chk)
            scroll_layout.addWidget(path_lbl)
            
        scroll_layout.addStretch()
        scroll.setWidget(card)
        layout.addWidget(scroll)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
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
    def __init__(self, watch_folders, use_chrono, routing_map, sort_ext, dashboard_db_path="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("FileOrganizerStealth - Settings")
        
        self.setWindowIcon(QIcon(ICON_PATH)) 
        self.setFixedSize(660, 760)
        
        self.setStyleSheet("""
            QDialog { background-color: #0b0b0d; }
            QWidget#scrollWidget { background-color: transparent; }

            QFrame#card {
                background-color: #16161a;
                border: 1px solid #26262b;
                border-radius: 10px;
            }

            QLabel#sectionTitle { color: #FFFFFF; font-size: 14px; font-weight: 700; }
            QLabel#sectionHint { color: #86868c; font-size: 11px; font-weight: 400; }
            QLabel#fieldLabel { color: #d9d9dc; font-size: 12px; font-weight: 600; }
            QLabel#dialogHeader { color: #FFFFFF; font-size: 19px; font-weight: 800; }
            QLabel#dialogSubheader { color: #86868c; font-size: 12px; font-weight: 400; }

            QLineEdit, QListWidget {
                background-color: #0b0b0d;
                color: #f2f2f2;
                border: 1px solid #2b2b30;
                border-radius: 6px;
                padding: 8px 10px;
                font-size: 12px;
                font-weight: 400;
            }
            QLineEdit:focus, QListWidget:focus { border: 1px solid #9c0b24; }
            QListWidget::item { padding: 3px 2px; }

            QPushButton {
                background-color: #7a0518;
                color: #FFFFFF;
                border: none;
                padding: 9px 16px;
                border-radius: 6px;
                font-weight: 600;
                font-size: 12px;
            }
            QPushButton:hover { background-color: #9c0b24; }
            QPushButton:pressed { background-color: #5c0210; }

            QPushButton#secondaryBtn {
                background-color: #232328;
                color: #e5e5e8;
                font-weight: 600;
            }
            QPushButton#secondaryBtn:hover { background-color: #2d2d33; }
            QPushButton#secondaryBtn:pressed { background-color: #1a1a1e; }

            QPushButton#scanBtn {
                background-color: #D69E00;
                color: #121212;
            }
            QPushButton#scanBtn:hover { background-color: #FFCC00; }

            QPushButton#saveBtn {
                background-color: #7F0002;
                font-size: 13.5px;
                font-weight: 700;
            }
            QPushButton#saveBtn:hover { background-color: #9c0b24; }

            QCheckBox { color: #e5e5e8; font-size: 12.5px; font-weight: 600; spacing: 10px; }
            QCheckBox#checkboxHint { color: #86868c; font-size: 11px; font-weight: 400; margin-left: 28px; }

            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical { border: none; background: transparent; width: 8px; margin: 0; }
            QScrollBar::handle:vertical { background: #333338; min-height: 24px; border-radius: 4px; }
            QScrollBar::handle:vertical:hover { background: #48484f; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
        """)

        self.watch_folders = watch_folders
        self.use_chrono = use_chrono
        self.routing_map = routing_map or {}
        self.sort_ext = sort_ext
        self.dashboard_db_path = dashboard_db_path or ""
        self.path_inputs = {}

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(24, 22, 24, 22)
        outer_layout.setSpacing(16)

        # ---- Header ------------------------------------------------------
        header = QLabel("Settings")
        header.setObjectName("dialogHeader")
        subheader = QLabel("Configure where FileOrganizerStealth watches and routes your files.")
        subheader.setObjectName("dialogSubheader")
        outer_layout.addWidget(header)
        outer_layout.addWidget(subheader)

        # Everything below the header scrolls as one column, so the window
        # itself stays a fixed, predictable size regardless of how many
        # routing categories exist.
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_widget.setObjectName("scrollWidget")
        main_layout = QVBoxLayout(scroll_widget)
        main_layout.setContentsMargins(0, 0, 4, 0)
        main_layout.setSpacing(14)

        # ---- Card: Watched Folders ----------------------------------------
        watch_card, watch_layout = self._card()
        watch_layout.addWidget(self._section_title("Watched Folders"))
        watch_layout.addWidget(self._section_hint("FileOrganizerStealth monitors these folders and sorts new files automatically."))

        watch_row = QHBoxLayout()
        watch_row.setSpacing(10)
        self.list_widget = QListWidget()
        self.list_widget.setFixedHeight(76)
        self.list_widget.addItems(self.watch_folders)
        watch_row.addWidget(self.list_widget)

        watch_btn_col = QVBoxLayout()
        watch_btn_col.setSpacing(8)
        btn_add = QPushButton("Add")
        btn_add.clicked.connect(self.add_watch_folder)
        btn_rem = QPushButton("Remove")
        btn_rem.setObjectName("secondaryBtn")
        btn_rem.clicked.connect(self.remove_watch_folder)
        watch_btn_col.addWidget(btn_add)
        watch_btn_col.addWidget(btn_rem)
        watch_btn_col.addStretch()
        watch_row.addLayout(watch_btn_col)
        watch_layout.addLayout(watch_row)
        main_layout.addWidget(watch_card)

        # ---- Card: Sorting Behavior ----------------------------------------
        behavior_card, behavior_layout = self._card()
        behavior_layout.addWidget(self._section_title("Sorting Behavior"))

        self.chk_ext = QCheckBox("Organize into exact file-type folders")
        self.chk_ext.setChecked(self.sort_ext)
        behavior_layout.addWidget(self.chk_ext)
        behavior_layout.addWidget(self._checkbox_hint("e.g. PDF/, DOCX/, ZIP/ instead of one general folder per category"))

        self.chk_chrono = QCheckBox("Enable chronological sub-folders")
        self.chk_chrono.setChecked(self.use_chrono)
        behavior_layout.addWidget(self.chk_chrono)
        behavior_layout.addWidget(self._checkbox_hint("Adds a Year/Month sub-folder inside each destination"))

        self.btn_scan = QPushButton("Smart Scan System for Existing Destinations")
        self.btn_scan.setObjectName("scanBtn")
        self.btn_scan.clicked.connect(self.run_smart_scan)
        behavior_layout.addWidget(self.btn_scan)
        main_layout.addWidget(behavior_card)

        # ---- Card: Dashboard Link ----------------------------------------
        dashboard_card, dashboard_layout = self._card()
        dashboard_layout.addWidget(self._section_title("FreelanceDashboard Link"))
        dashboard_layout.addWidget(self._section_hint("Optional - matches organized files to projects/clients in freelance.db"))

        db_row = QHBoxLayout()
        db_row.setSpacing(10)
        self.txt_db_path = QLineEdit()
        self.txt_db_path.setText(self.dashboard_db_path)
        self.txt_db_path.setPlaceholderText("Path to freelance.db")
        db_row.addWidget(self.txt_db_path)
        btn_db_browse = QPushButton("Browse")
        btn_db_browse.setObjectName("secondaryBtn")
        btn_db_browse.setFixedWidth(90)
        btn_db_browse.clicked.connect(self.browse_dashboard_db)
        db_row.addWidget(btn_db_browse)
        dashboard_layout.addLayout(db_row)
        main_layout.addWidget(dashboard_card)

        # ---- Card: Startup & Diagnostics ----------------------------------------
        startup_card, startup_layout = self._card()
        startup_layout.addWidget(self._section_title("Startup & Diagnostics"))

        self.chk_startup = QCheckBox("Launch automatically when Windows starts")
        if startup_manager.is_available():
            self.chk_startup.setChecked(startup_manager.is_startup_enabled())
            startup_layout.addWidget(self.chk_startup)
            startup_layout.addWidget(self._checkbox_hint("Runs silently in the tray at login - no console window"))
        else:
            self.chk_startup.setChecked(False)
            self.chk_startup.setEnabled(False)
            startup_layout.addWidget(self.chk_startup)
            startup_layout.addWidget(self._checkbox_hint("Only available on Windows"))

        logs_row = QHBoxLayout()
        logs_row.setSpacing(10)
        logs_hint = self._section_hint("Errors and file moves are written to stealth_organizer.log")
        btn_view_logs = QPushButton("View Logs")
        btn_view_logs.setObjectName("secondaryBtn")
        btn_view_logs.setFixedWidth(120)
        btn_view_logs.clicked.connect(self.view_logs)
        logs_row.addWidget(logs_hint, stretch=1)
        logs_row.addWidget(btn_view_logs)
        startup_layout.addLayout(logs_row)
        main_layout.addWidget(startup_card)

        # ---- Card: Custom Destinations ----------------------------------------
        routing_card, routing_layout = self._card()
        routing_layout.addWidget(self._section_title("Custom Destinations"))
        routing_layout.addWidget(self._section_hint("Leave a category blank to sort it locally inside the watched folder."))

        for i, cat in enumerate(CATEGORIES_LIST):
            if i > 0:
                divider = QFrame()
                divider.setFixedHeight(1)
                divider.setStyleSheet("background-color: #232328; border: none;")
                routing_layout.addWidget(divider)

            row = QHBoxLayout()
            row.setSpacing(10)
            lbl = QLabel(cat)
            lbl.setObjectName("fieldLabel")
            lbl.setFixedWidth(100)

            txt = QLineEdit()
            txt.setText(self.routing_map.get(cat, ""))
            txt.setPlaceholderText("Sort locally")
            self.path_inputs[cat] = txt

            btn = QPushButton("Browse")
            btn.setObjectName("secondaryBtn")
            btn.setFixedWidth(90)
            btn.clicked.connect(lambda checked, c=cat, t=txt: self.browse_category(c, t))

            row.addWidget(lbl)
            row.addWidget(txt)
            row.addWidget(btn)
            routing_layout.addLayout(row)

        main_layout.addWidget(routing_card)
        main_layout.addStretch()

        scroll.setWidget(scroll_widget)
        outer_layout.addWidget(scroll)

        self.btn_save = QPushButton("Save & Apply")
        self.btn_save.setObjectName("saveBtn")
        self.btn_save.setFixedHeight(46)
        self.btn_save.clicked.connect(self.save_and_close)
        outer_layout.addWidget(self.btn_save)

    # ---- Style helpers ----------------------------------------------------
    def _card(self):
        frame = QFrame()
        frame.setObjectName("card")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(10)
        return frame, layout

    def _section_title(self, text):
        lbl = QLabel(text)
        lbl.setObjectName("sectionTitle")
        return lbl

    def _section_hint(self, text):
        lbl = QLabel(text)
        lbl.setObjectName("sectionHint")
        lbl.setWordWrap(True)
        return lbl

    def _checkbox_hint(self, text):
        lbl = QLabel(text)
        lbl.setObjectName("checkboxHint")
        lbl.setWordWrap(True)
        return lbl

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

    def browse_dashboard_db(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select freelance.db", "", "SQLite Database (*.db)")
        if file_path:
            self.txt_db_path.setText(file_path)

    def view_logs(self):
        if not os.path.exists(LOG_PATH):
            QMessageBox.information(self, "No Logs Yet", "No log entries have been written yet. This appears once the watcher records its first event.")
            return
        try:
            os.startfile(LOG_PATH)
        except Exception as e:
            QMessageBox.warning(self, "Couldn't Open Log", f"Could not open the log file automatically.\n\nLocation: {LOG_PATH}\nError: {e}")

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
        self.dashboard_db_path = self.txt_db_path.text().strip()

        if startup_manager.is_available():
            if self.chk_startup.isChecked():
                if not startup_manager.enable_startup(MAIN_PY_PATH):
                    logger.warning("Failed to enable startup registry entry")
                    QMessageBox.warning(self, "Startup Failed", "Could not update the Windows registry to enable auto-start. Check your permissions.")
                    self.chk_startup.setChecked(False)
            else:
                if not startup_manager.disable_startup():
                    logger.warning("Failed to disable startup registry entry")
                    QMessageBox.warning(self, "Startup Failed", "Could not update the Windows registry to disable auto-start. Check your permissions.")
                    self.chk_startup.setChecked(True)

        self.accept()

class WatcherThread(QThread):
    # Emitted from the background thread whenever a file is organized and
    # matched to a dashboard project/client. Qt signals are thread-safe to
    # emit from any thread; connect() in the GUI thread handles the marshal.
    file_organized = pyqtSignal(str)

    def __init__(self, watch_folders, use_chronological, routing_map, sort_by_extension, dashboard_db_path=None):
        super().__init__()
        self.watch_folders = watch_folders
        self.use_chronological = use_chronological
        self.routing_map = routing_map
        self.sort_by_extension = sort_by_extension
        self.dashboard_db_path = dashboard_db_path
        self.watcher = BackgroundWatcher(
            self.watch_folders,
            self.use_chronological,
            self.routing_map,
            self.sort_by_extension,
            dashboard_db_path=self.dashboard_db_path,
            on_file_organized=self.file_organized.emit,
        )

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
        self.watch_folders, self.use_chronological, self.routing_map, self.sort_by_extension, self.dashboard_db_path = self.load_config()
        logger.info("FileOrganizerStealth starting up")
        
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
                        data.get("sort_by_extension", False),
                        data.get("dashboard_db_path", "")
                    )
            except Exception:
                pass
        return [], True, {}, False, ""

    def save_config(self, folders, chrono, routing_map, sort_ext, dashboard_db_path=""):
        with open(CONFIG_PATH, "w") as f:
            json.dump({
                "watch_folders": folders, 
                "use_chronological": chrono,
                "routing_map": routing_map,
                "sort_by_extension": sort_ext,
                "dashboard_db_path": dashboard_db_path
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
        dialog = SettingsWindow(self.watch_folders, self.use_chronological, self.routing_map, self.sort_by_extension, self.dashboard_db_path)
        if dialog.exec(): 
            self.watch_folders = dialog.watch_folders
            self.use_chronological = dialog.use_chrono
            self.routing_map = dialog.routing_map
            self.sort_by_extension = dialog.sort_ext
            self.dashboard_db_path = dialog.dashboard_db_path
            
            self.save_config(self.watch_folders, self.use_chronological, self.routing_map, self.sort_by_extension, self.dashboard_db_path)
            
            if self.watch_folders:
                self.tray.setToolTip(f"FileOrganizerStealth Active\nWatching {len(self.watch_folders)} folder(s)")
                self.start_watching()

    def start_watching(self):
        if self.thread and self.thread.isRunning():
            self.thread.stop()
            
        if self.watch_folders:
            self.thread = WatcherThread(
                self.watch_folders,
                self.use_chronological,
                self.routing_map,
                self.sort_by_extension,
                dashboard_db_path=self.dashboard_db_path,
            )
            self.thread.file_organized.connect(self.show_organize_alert)
            self.thread.start()
            self.tray.showMessage("FileOrganizerStealth Active", f"Silently organizing {len(self.watch_folders)} folder(s)", QSystemTrayIcon.MessageIcon.Information, 2000)

    def show_organize_alert(self, message):
        self.tray.showMessage("Stealth Organizer", f"Organized: {message}", QSystemTrayIcon.MessageIcon.Information, 3000)

    def quit_app(self):
        logger.info("FileOrganizerStealth shutting down")
        if self.thread and self.thread.isRunning():
            self.thread.stop()
        self.tray.hide()
        self.app.quit()

if __name__ == "__main__":
    organizer = StealthOrganizer()
    sys.exit(organizer.app.exec())