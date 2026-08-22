# FileOrganizerStealth

A silent, background-running desktop utility built with PyQt6 that automatically organizes files across your entire system.

Unlike standard file managers, FileOrganizerStealth runs invisibly in the system tray, watching high-traffic directories (like Downloads) and instantly routing files to custom local or cloud destinations based on their exact file type.

---

## Features

* Watch multiple high-traffic folders simultaneously
* Map specific file categories (Images, Documents, Code) to custom drives or cloud folders
* Dynamically generate exact file-type folders (e.g., `PDF/`, `DOCX/`)
* Smart System Scan to automatically find existing Windows and OneDrive destination folders
* Chronological sub-sorting to organize files by `Year/Month`
* Stealth operation via the Windows system tray with zero desktop clutter
* Built-in collision handling and safety nets to skip locked files
* Skips files that are still actively downloading, even ones that write directly to their final extension instead of a `.part`/`.crdownload` staging name
* Optional launch at Windows login, registered silently via the registry (no console window)
* Rotating log file (`stealth_organizer.log`) with a one-click "View Logs" button, since a tray app has no visible console
* Optional link to a [FreelanceDashboard](../FreelanceDashboard) instance: organized files are matched to active projects/clients by filename and logged to a shared SQLite database for the dashboard to pick up

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt

```

### 2. Run the app

```bash
python src/main.py

```

To run without a console window (recommended for everyday use), launch with `pythonw` instead:

```bash
pythonw src/main.py

```

This is also exactly what happens automatically if you enable **Launch automatically when Windows starts** in Settings.

---

## Config Format

The app saves your routing preferences in a `config.json` file in the root directory. Settings update automatically when using the UI, but you can also edit this file directly:

```json
{
    "watch_folders": [
        "C:/Users/saidm/Downloads"
    ],
    "use_chronological": false,
    "routing_map": {
        "Images": "C:\\Users\\saidm\\OneDrive\\Pictures",
        "Documents": "C:\\Users\\saidm\\OneDrive\\Documents",
        "Code": "C:\\Users\\saidm\\OneDrive\\Documents\\VS code",
        "Archives": "C:\\Users\\saidm\\OneDrive\\Documents"
    },
    "sort_by_extension": true,
    "dashboard_db_path": "C:\\Users\\saidm\\OneDrive\\Documents\\VS code\\FreelanceDashboard\\data\\freelance.db"
}

```

Notes:

* If a category is left out of `routing_map` (or left blank in the UI), files of that type will be sorted locally inside the watched folder.
* `sort_by_extension` forces the engine to append exact folders (like `\ZIP`) to the end of the routing path.
* `dashboard_db_path` is optional. Leave it blank (or omit it) to run the organizer standalone with no dashboard integration.

---

## Supported File Types

The engine automatically recognizes and categorizes:

* **Images**: `.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.webp`, `.svg`, `.heic`, `.tiff`
* **Documents**: `.pdf`, `.docx`, `.txt`, `.rtf`, `.odt`, `.doc`
* **Spreadsheets**: `.xlsx`, `.csv`, `.xls`, `.ods`
* **Presentations**: `.pptx`, `.ppt`, `.odp`
* **Code**: `.py`, `.js`, `.html`, `.css`, `.cpp`, `.json`, `.yaml`, `.sql`, etc.
* **Archives**: `.zip`, `.rar`, `.7z`, `.tar`, `.gz`
* **Videos**: `.mp4`, `.mkv`, `.avi`, `.mov`, `.wmv`, `.flv`
* **Audio**: `.mp3`, `.wav`, `.aac`, `.flac`, `.ogg`, `.m4a`
* **Executables**: `.exe`, `.msi`, `.apk`, `.bat`
* **Fonts**: `.ttf`, `.otf`

Files still being downloaded are skipped rather than moved mid-write. Anything with a `.crdownload`, `.part`, `.tmp`, or `.download` extension is ignored outright; anything else that was modified in the last 10 seconds gets a quick size-stability check (if its size is still changing, it's skipped and retried on the next poll cycle).

---

## FreelanceDashboard Integration (optional)

If you point **FreelanceDashboard Database** (in Settings) at a `freelance.db` file shared with a [FreelanceDashboard](../FreelanceDashboard) JavaFX app, every file the organizer moves is additionally:

1. Matched against that database's active projects/clients by filename (whole-word match, so "App" won't match "Apple")
2. Typed as `INVOICE`, `CONTRACT`, `ASSET`, or `GENERAL` based on filename keywords
3. Logged to a `project_documents` table in the shared SQLite database, in WAL mode so both apps can read/write concurrently without locking each other out

This is purely additive metadata for the dashboard to consume — it does **not** change where files physically land; your `routing_map`, chronological sub-folders, and extension folders all behave exactly as configured regardless of whether a dashboard is linked.

Leave the field blank to run fully standalone.

---

## Logging

All lifecycle events, file moves, skips, and errors are written to `stealth_organizer.log` in the project root, since the tray app has no visible console to print to. The log rotates automatically at 2MB (keeping 3 backups) so it won't grow unbounded.

Open it directly via **Settings → Startup & Diagnostics → View Logs**, or from the file itself.

---

## Usage

* **Open Settings**: Right-click the tray icon and select "Settings"
* **Watched Folders**: Add or remove the folders the app monitors
* **Sorting Behavior**: Toggle exact file-type folders and chronological (`Year/Month`) sub-sorting, or run a Smart Scan to auto-detect existing Windows/OneDrive destinations
* **FreelanceDashboard Link**: Optionally point at a shared `freelance.db` to log organized files against your projects
* **Startup & Diagnostics**: Enable launch-at-login, or open the log file
* **Custom Destinations**: Leave a category blank to sort locally, or click "Browse" to set a global destination
* **Quit**: Right-click the tray icon and select "Quit Organizer" to safely stop the background thread

---

## Requirements

* Python 3.9+
* Windows (the tray integration, startup registration via the registry, and log-file opening are all Windows-specific)
* PyQt6

See `requirements.txt` for the exact pinned dependency. Everything else the app uses (`sqlite3`, `winreg`, `logging`, `threading`) is part of the Python standard library — no extra installs needed for logging, startup registration, or the dashboard bridge.
