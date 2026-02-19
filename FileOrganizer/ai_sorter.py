import shutil
from pathlib import Path

CATEGORIES = {

    # Images
    ".jpg": "Images",
    ".jpeg": "Images",
    ".png": "Images",
    ".gif": "Images",
    ".bmp": "Images",
    ".webp": "Images",
    ".svg": "Images",
    ".heic": "Images",
    ".tiff": "Images",

    # Documents
    ".pdf": "Documents",
    ".doc": "Documents",
    ".docx": "Documents",
    ".txt": "Documents",
    ".rtf": "Documents",
    ".odt": "Documents",

    # Spreadsheets
    ".xls": "Spreadsheets",
    ".xlsx": "Spreadsheets",
    ".csv": "Spreadsheets",
    ".ods": "Spreadsheets",

    # Presentations
    ".ppt": "Presentations",
    ".pptx": "Presentations",
    ".odp": "Presentations",

    # Code
    ".py": "Code",
    ".js": "Code",
    ".ts": "Code",
    ".html": "Code",
    ".css": "Code",
    ".cpp": "Code",
    ".c": "Code",
    ".java": "Code",
    ".json": "Code",
    ".xml": "Code",
    ".yaml": "Code",
    ".yml": "Code",
    ".sql": "Code",

    # Archives
    ".zip": "Archives",
    ".rar": "Archives",
    ".7z": "Archives",
    ".tar": "Archives",
    ".gz": "Archives",

    # Videos
    ".mp4": "Videos",
    ".mkv": "Videos",
    ".avi": "Videos",
    ".mov": "Videos",
    ".wmv": "Videos",
    ".flv": "Videos",

    # Audio
    ".mp3": "Audio",
    ".wav": "Audio",
    ".aac": "Audio",
    ".flac": "Audio",
    ".ogg": "Audio",
    ".m4a": "Audio",

    # Executables
    ".exe": "Executables",
    ".msi": "Executables",
    ".apk": "Executables",
    ".bat": "Executables",

    # Fonts
    ".ttf": "Fonts",
    ".otf": "Fonts",
}


def sort_folder(folder):
    folder = Path(folder)
    actions = []

    for file in folder.iterdir():
        if file.is_file():
            ext = file.suffix.lower()
            category = CATEGORIES.get(ext, "Others")

            target_dir = folder / category
            target_dir.mkdir(exist_ok=True)

            new_path = target_dir / file.name

            if file != new_path:
                shutil.move(str(file), new_path)
                actions.append(f"Moved: {file.name} → {category}/")

    return actions
