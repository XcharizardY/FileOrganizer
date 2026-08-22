"""
DashboardBridge - shared SQLite bridge between FileOrganizerStealth (Python)
and FreelanceDashboard (JavaFX).

Both apps read/write the same freelance.db, so this module configures WAL
mode for concurrent access and exposes the two operations the organizer
needs: reading active projects/clients (to match filenames against) and
logging a routed file so the JavaFX dashboard can pick it up.
"""

import sqlite3
from typing import List, Dict, Optional

from logger_setup import get_logger

logger = get_logger()

SCHEMA = """
CREATE TABLE IF NOT EXISTS project_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER,
    client_id INTEGER,
    file_name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_type TEXT,
    category TEXT,
    status TEXT DEFAULT 'NEW',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE SET NULL,
    FOREIGN KEY(client_id) REFERENCES clients(id) ON DELETE SET NULL
);
"""


class DashboardBridge:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._ensure_schema()

    def _get_connection(self) -> sqlite3.Connection:
        # 10s timeout lets Python wait if the JavaFX app is mid-write.
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA busy_timeout = 5000;")
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_schema(self):
        try:
            with self._get_connection() as conn:
                conn.executescript(SCHEMA)
        except Exception as e:
            logger.error(f"Failed to ensure schema: {e}")

    def get_active_projects(self) -> List[Dict]:
        """Fetch active projects + client names to match against filenames."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                query = """
                    SELECT p.id AS project_id, p.name AS project_name,
                           c.id AS client_id, c.name AS client_name
                    FROM projects p
                    LEFT JOIN clients c ON p.client_id = c.id
                    WHERE p.status != 'Completed'
                """
                return [dict(row) for row in cursor.execute(query).fetchall()]
        except Exception as e:
            logger.error(f"Failed to fetch active projects: {e}")
            return []

    def log_document(self, project_id: Optional[int], client_id: Optional[int],
                      file_name: str, dest_path: str, category: str,
                      file_type: Optional[str] = None) -> None:
        """Insert a routed-file record for the JavaFX dashboard to consume."""
        try:
            with self._get_connection() as conn:
                conn.execute("""
                    INSERT INTO project_documents
                    (project_id, client_id, file_name, file_path, file_type, category, status)
                    VALUES (?, ?, ?, ?, ?, ?, 'NEW')
                """, (project_id, client_id, file_name, dest_path, file_type, category))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to log document '{file_name}': {e}")
