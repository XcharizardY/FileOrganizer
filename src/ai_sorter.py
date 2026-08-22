import re
import shutil
import time
import datetime
from pathlib import Path

from logger_setup import get_logger

logger = get_logger()

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

# Keyword-based document typing for dashboard logging (separate from the
# extension-based CATEGORIES used for physical routing above).
DOCUMENT_TYPES = {
    "INVOICE": ["invoice", "bill", "receipt"],
    "CONTRACT": ["contract", "agreement", "nda", "sow"],
    "ASSET": ["mockup", "wireframe", "logo", "design"],
}


def resolve_metadata(filename: str, active_projects: list) -> tuple:
    """Returns (doc_category, project_id, client_id, project_name) based on
    keyword/regex matching of the filename. Does NOT affect where the file
    is physically moved - it's metadata for the dashboard DB log only."""
    name_lower = filename.lower()

    doc_category = "GENERAL"
    for cat, keywords in DOCUMENT_TYPES.items():
        if any(kw in name_lower for kw in keywords):
            doc_category = cat
            break

    project_id, client_id, project_name = None, None, None
    for p in active_projects or []:
        p_name = str(p.get("project_name") or "").lower()
        c_name = str(p.get("client_name") or "").lower()

        # \b enforces whole-word matches so "App" doesn't match "Apple"
        if (p_name and re.search(rf"\b{re.escape(p_name)}\b", name_lower)) or \
           (c_name and re.search(rf"\b{re.escape(c_name)}\b", name_lower)):
            project_id = p.get("project_id")
            client_id = p.get("client_id")
            project_name = p.get("project_name")
            break

    return doc_category, project_id, client_id, project_name

def get_unique_path(target_dir, filepath):
    base_name = filepath.stem
    ext = filepath.suffix
    counter = 1
    new_path = target_dir / filepath.name
    while new_path.exists():
        new_path = target_dir / f"{base_name} ({counter}){ext}"
        counter += 1
    return new_path


def is_file_stable(file_path: Path, wait_seconds: float = 1.0) -> bool:
    """Guards against apps that write straight to a final extension
    (no .part/.crdownload staging name) rather than locking the file.

    Only files modified in the last 10 seconds actually pay the 1s wait -
    anything older is already-settled and gets skipped instantly. Without
    that shortcut, every file in the watched folder would eat a 1s sleep
    on every single 5s poll cycle, which for a folder with 20+ files would
    make the watcher fall permanently behind its own polling interval.
    """
    try:
        stat_before = file_path.stat()
    except OSError:
        return False

    if time.time() - stat_before.st_mtime > 10:
        return True

    size_before = stat_before.st_size
    time.sleep(wait_seconds)

    try:
        size_after = file_path.stat().st_size
    except OSError:
        # File vanished mid-check (e.g. renamed by the downloader) - treat
        # as unstable so this cycle skips it rather than crashing.
        return False

    return size_before == size_after

def sort_folder(folder, use_chronological=True, routing_map=None, sort_by_extension=False, active_projects=None):
    folder = Path(folder)
    routing_map = routing_map or {}
    active_projects = active_projects or []
    actions = []

    # iterdir() only looks at the top layer. We explicitly check is_file() 
    # so it completely ignores any existing folders inside Downloads.
    for file in folder.iterdir():
        if not file.is_file():
            continue

        ext = file.suffix.lower()
        if ext in IGNORED_EXTENSIONS or not ext:
            continue

        if not is_file_stable(file):
            logger.info(f"Skipping '{file.name}' - still being written, will retry next cycle")
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

        # Resolve dashboard metadata (project/client/doc-type) - this is
        # purely informational and never changes target_dir above.
        doc_category, project_id, client_id, project_name = resolve_metadata(file.name, active_projects)

        try:
            target_dir.mkdir(parents=True, exist_ok=True)
            new_path = get_unique_path(target_dir, file)
            
            if file != new_path:
                shutil.move(str(file), new_path)
                actions.append({
                    "filename": file.name,
                    "dest_path": str(new_path),
                    "file_type": ext,
                    "base_category": base_category,
                    "doc_category": doc_category,
                    "project_id": project_id,
                    "client_id": client_id,
                    "project_name": project_name,
                })
        except Exception as e:
            logger.error(f"Error moving '{file.name}': {e}")

    return actions