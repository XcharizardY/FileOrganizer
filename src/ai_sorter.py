import shutil
import datetime
from pathlib import Path

CATEGORIES = {
    ".jpg": "Images", ".jpeg": "Images", ".png": "Images", ".gif": "Images", ".bmp": "Images", ".webp": "Images", ".svg": "Images", ".heic": "Images", ".tiff": "Images",
    ".pdf": "Documents", ".doc": "Documents", ".docx": "Documents", ".txt": "Documents", ".rtf": "Documents", ".odt": "Documents",
    ".xls": "Spreadsheets", ".xlsx": "Spreadsheets", ".csv": "Spreadsheets", ".ods": "Spreadsheets",
    ".ppt": "Presentations", ".pptx": "Presentations", ".odp": "Presentations",
    ".py": "Code", ".js": "Code", ".ts": "Code", ".html": "Code", ".css": "Code", ".cpp": "Code", ".c": "Code", ".java": "Code", ".json": "Code", ".xml": "Code", ".yaml": "Code", ".yml": "Code", ".sql": "Code",
    ".zip": "Archives", ".rar": "Archives", ".7z": "Archives", ".tar": "Archives", ".gz": "Archives",
    ".mp4": "Videos", ".mkv": "Videos", ".avi": "Videos", ".mov": "Videos", ".wmv": "Videos", ".flv": "Videos",
    ".mp3": "Audio", ".wav": "Audio", ".aac": "Audio", ".flac": "Audio", ".ogg": "Audio", ".m4a": "Audio",
    ".exe": "Executables", ".msi": "Executables", ".apk": "Executables", ".bat": "Executables",
    ".ttf": "Fonts", ".otf": "Fonts",
}

IGNORED_EXTENSIONS = {".crdownload", ".part", ".tmp", ".download"}

def get_unique_path(target_dir, filepath):
    base_name = filepath.stem
    ext = filepath.suffix
    counter = 1
    new_path = target_dir / filepath.name
    while new_path.exists():
        new_path = target_dir / f"{base_name} ({counter}){ext}"
        counter += 1
    return new_path

def sort_folder(folder, use_chronological=True, routing_map=None, sort_by_extension=False):
    folder = Path(folder)
    routing_map = routing_map or {}
    actions = []

    # iterdir() only looks at the top layer. We explicitly check is_file() 
    # so it completely ignores any existing folders inside Downloads.
    for file in folder.iterdir():
        if not file.is_file():
            continue

        ext = file.suffix.lower()
        if ext in IGNORED_EXTENSIONS or not ext:
            continue

        base_category = CATEGORIES.get(ext, "Others")
        custom_path = routing_map.get(base_category)

        # Build the target path
        if sort_by_extension:
            ext_folder_name = ext.replace(".", "").upper()
            if custom_path:
                target_dir = Path(custom_path) / ext_folder_name
            else:
                target_dir = folder / ext_folder_name
        else:
            if custom_path:
                target_dir = Path(custom_path)
            else:
                target_dir = folder / base_category

        if use_chronological:
            timestamp = file.stat().st_mtime 
            date_subfolder = datetime.datetime.fromtimestamp(timestamp).strftime("%Y/%B")
            target_dir = target_dir / date_subfolder

        try:
            target_dir.mkdir(parents=True, exist_ok=True)
            new_path = get_unique_path(target_dir, file)
            
            if file != new_path:
                shutil.move(str(file), new_path)
                actions.append(f"Moved: {file.name} → {target_dir}")
        except Exception as e:
            print(f"Error moving {file.name}: {e}")

    return actions