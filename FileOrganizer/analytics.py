from collections import defaultdict
from pathlib import Path
import os


class Analytics:
    def __init__(self, folder):
        self.folder = Path(folder)

    def stats(self):
        total_files = 0
        total_size = 0
        types = defaultdict(int)

        for file in self.folder.rglob("*"):
            if file.is_file():
                total_files += 1
                total_size += file.stat().st_size
                types[file.suffix.lower()] += 1

        return {
            "total_files": total_files,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "types": dict(types)
        }
