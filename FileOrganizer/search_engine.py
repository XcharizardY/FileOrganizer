import os
import re
from collections import defaultdict


class SearchEngine:
    def __init__(self):
        # token -> set(filepaths)
        self.index = defaultdict(set)
        self.files = set()

    # ---------------------------
    # Build index for a folder
    # ---------------------------
    def index_folder(self, folder_path):
        self.index.clear()
        self.files.clear()

        for root, _, files in os.walk(folder_path):
            for file in files:
                full_path = os.path.join(root, file)
                self.files.add(full_path)
                self._index_file(full_path)

    # ---------------------------
    # Index a single file
    # ---------------------------
    def _index_file(self, filepath):
        filename = os.path.basename(filepath).lower()

        # Split by space, dash, underscore, dot
        tokens = re.split(r"[\\s._-]+", filename)

        for token in tokens:
            if token:
                self.index[token].add(filepath)

        # Also index full filename
        self.index[filename].add(filepath)

    # ---------------------------
    # Remove file (for watcher)
    # ---------------------------
    def remove_file(self, filepath):
        for token in list(self.index.keys()):
            if filepath in self.index[token]:
                self.index[token].remove(filepath)
                if not self.index[token]:
                    del self.index[token]

        self.files.discard(filepath)

    # ---------------------------
    # Search (partial + exact)
    # ---------------------------
    def search(self, query):
        query = query.lower().strip()
        if not query:
            return []

        results = set()

        # Exact token match
        if query in self.index:
            results |= self.index[query]

        # Partial match (zip → .zip, win → winrar)
        for token, paths in self.index.items():
            if query in token:
                results |= paths

        return sorted(results)
