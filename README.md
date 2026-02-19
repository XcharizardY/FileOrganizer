# AI Smart File Organizer

A desktop application built with **PyQt6** that automatically organizes files, provides smart search functionality, and displays folder analytics in a modern dark-themed interface.

---

## Features

### 1. Folder Selection

* Select any directory on your system.
* Automatically indexes files for fast searching.
* Displays files with categorized icons.

### 2. Smart Search

* Real-time file search.
* Fast indexed lookup.
* Results update instantly as you type.

### 3. Background File Monitoring

* Runs in a separate thread.
* Watches selected folder for changes.
* Prevents UI freezing.

### 4. File Analytics

* Displays:

  * Total number of files
  * Total folder size (MB)
  * Individual file sizes (KB)

### 5. File Type Recognition

Automatic icon assignment for:

* Images (`.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`)
* Documents (`.pdf`, `.docx`, `.txt`)
* Spreadsheets (`.xlsx`, `.csv`)
* Presentations (`.pptx`)
* Code files (`.py`, `.js`, `.html`, `.css`, etc.)
* Archives (`.zip`, `.rar`)
* Videos (`.mp4`, `.mkv`)
* Audio (`.mp3`, `.wav`)
* Executables (`.exe`)
* Fonts (`.ttf`, `.otf`)
* Default fallback icon

---

## Project Structure

```
AI-Smart-File-Organizer/
│
├── main.py                  # Main GUI application
├── background_watcher.py    # Folder monitoring logic
├── search_engine.py         # File indexing and search
├── analytics.py             # File statistics module
├── ai_sorter.py             # AI-based file sorting logic
├── cloud_sync.py            # Cloud integration module
├── icons/                   # SVG icons for file types
└── README.md
```

---

## Requirements

* Python 3.9+
* PyQt6

Install dependencies:

```bash
pip install PyQt6
```

---

## How to Run

```bash
python main.py
```

---

## How It Works

1. User selects a folder.
2. The folder is indexed using `SearchEngine`.
3. Files are displayed with icons.
4. A background thread monitors changes.
5. Analytics are calculated recursively.
6. Smart search queries use the indexed data.

---

## Architecture Overview

* **UI Layer** – `main.py`
* **Search Engine** – Handles indexing and searching
* **Background Watcher** – Monitors folder changes via QThread
* **Analytics Module** – Calculates size and file counts
* **AI Sorter (Optional Extension)** – File categorization logic
* **Cloud Sync (Optional Extension)** – Future cloud integration

---

## Known Improvements

* Connect unused modules (`cloud_sync.py`, `ai_sorter.py`)
* Improve error handling for invalid folders
* Add stop button for background watcher
* Use `Analytics` class instead of manual calculation
* Implement full AI auto-sorting workflow

---

## License

This project is for educational and development purposes.
