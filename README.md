# FileOrganizerStealth

A silent, background-running desktop utility built with **PyQt6**[cite: 7] that automatically organizes files across your entire system. Unlike standard file managers, FileOrganizerStealth runs invisibly in the system tray, watching high-traffic directories and instantly routing files to custom local or cloud destinations.

---

## ⚡ Core Features

### 1. Stealth Operation
* Runs completely in the background via the Windows system tray.
* Zero desktop clutter and no persistent open windows.
* Prevents UI freezing by handling all sorting in an isolated background thread[cite: 7].

### 2. Global File Routing
* Map specific file categories (Images, Documents, Code, Archives) to entirely different drives or sync folders (like OneDrive).
* Automatically catches and relocates files the second they land in a watched folder.

### 3. Precision Sorting (Exact File Type)
* Dynamically generates folders based on exact file extensions.
* Example: A `.pptx` file dropped in `Downloads` is instantly routed to `OneDrive\Documents\PPTX\`.

### 4. Smart System Scan
* One-click configuration.
* Automatically scans your system for standard Windows and OneDrive directories (Pictures, Music, Documents, VS Code projects) and maps them to the routing engine automatically.

### 5. Multi-Directory Monitoring
* Watch multiple folders (e.g., `Downloads`, `Desktop`, and `Documents`) simultaneously.

### 6. Chronological Sub-Sorting
* Optional toggle to automatically generate `Year/Month` sub-folders inside your destination directories.

---

## 📂 Architecture & File Structure

```text
FileOrganizer/
│
├── assets/
│   └── tray_icon.svg            # Professional system tray and app icon
├── src/
│   ├── main.py                  # UI Control Panel and System Tray initialization
│   ├── background_watcher.py    # Multi-folder background monitoring thread
│   └── ai_sorter.py             # Core logic for routing, collisions, and extensions
├── config.json                  # Persistent save state for routing maps and toggles
├── requirements.txt             # Project dependencies
└── README.md

```

---

## 🛠️ Supported File Types

The engine automatically recognizes and categorizes:

* **Images**: `.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.webp`, `.svg`, `.heic`, `.tiff`
* **Documents**: `.pdf`, `.docx`, `.txt`, `.rtf`, `.odt`, `.doc`
* **Spreadsheets**: `.xlsx`, `.csv`, `.xls`, `.ods`
* **Presentations**: `.pptx`, `.ppt`, `.odp`
* **Code files**: `.py`, `.js`, `.html`, `.css`, `.cpp`, `.json`, `.yaml`, `.sql`, etc.
* **Archives**: `.zip`, `.rar`, `.7z`, `.tar`, `.gz`
* **Videos**: `.mp4`, `.mkv`, `.avi`, `.mov`, `.wmv`, `.flv`
* **Audio**: `.mp3`, `.wav`, `.aac`, `.flac`, `.ogg`, `.m4a`
* **Executables**: `.exe`, `.msi`, `.apk`, `.bat`
* **Fonts**: `.ttf`, `.otf`

---

## 🚀 Installation & Setup

**Requirements:**

* Python 3.9+


* PyQt6



**1. Install Dependencies:**

```bash
pip install -r requirements.txt

```

**2. Run the Application:**

```bash
python src/main.py

```

**3. Configuration:**

* Right-click the folder icon in your system tray and select **Settings**.
* Click **Smart Scan** to auto-fill your standard Windows paths.
* Add your `Downloads` or `Desktop` to the "Folders to Watch" list.
* Click **Save & Apply**. The app will now silently organize your files in the background.

```