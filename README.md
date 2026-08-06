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
    "sort_by_extension": true
}

```

Notes:

* If a category is left out of `routing_map` (or left blank in the UI), files of that type will be sorted locally inside the watched folder.
* `sort_by_extension` forces the engine to append exact folders (like `\ZIP`) to the end of the routing path.

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

---

## Usage

* **Open Settings**: Right-click the folder icon in your system tray and select "Settings"
* **Smart Scan**: Click the scan button to automatically link your standard Windows and OneDrive paths
* **Add Folders**: Click "Add" to select directories you want the app to monitor
* **Custom Destinations**: Leave a category blank to sort locally, or click "Browse" to set a global destination
* **Quit**: Right-click the tray icon and select "Quit Organizer" to safely stop the background thread

---

## Requirements

* Python 3.9+
* PyQt6