"""
logger_setup.py - centralized logging for FileOrganizerStealth.

The app runs headless in the system tray with no attached console, so
print() output goes nowhere. This configures a single rotating log file
that every module imports and writes to instead.
"""

import logging
import os
from logging.handlers import RotatingFileHandler

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SRC_DIR)
LOG_PATH = os.path.join(PROJECT_ROOT, "stealth_organizer.log")

_logger = None


def get_logger() -> logging.Logger:
    """Returns the shared app logger, configuring it on first call.

    Guarded so repeated imports (main.py, ai_sorter.py, background_watcher.py,
    dashboard_bridge.py) don't each attach their own duplicate file handler,
    which would otherwise write every log line multiple times.
    """
    global _logger
    if _logger is not None:
        return _logger

    logger = logging.getLogger("stealth_organizer")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        # 2MB x 3 backups keeps this from growing unbounded on a machine
        # that stays logged in for weeks, while still holding plenty of
        # history for debugging a "why didn't this file move" report.
        handler = RotatingFileHandler(LOG_PATH, maxBytes=2 * 1024 * 1024, backupCount=3, encoding="utf-8")
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s", "%Y-%m-%d %H:%M:%S")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    _logger = logger
    return _logger
