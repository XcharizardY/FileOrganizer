"""
startup_manager.py - registers/unregisters FileOrganizerStealth to launch
automatically at Windows login via HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run.

HKCU (not HKLM) is used deliberately: it requires no admin elevation and
only affects the current user, which is the correct scope for a personal
tray utility.
"""

import os
import sys

APP_NAME = "FileOrganizerStealth"
RUN_KEY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"

try:
    import winreg
    _WINREG_AVAILABLE = True
except ImportError:
    # winreg only exists on Windows. Every other function below degrades
    # to a safe no-op if this is False, rather than crashing on import.
    _WINREG_AVAILABLE = False


def is_available() -> bool:
    """False on non-Windows platforms - callers should hide/disable the
    'run at startup' UI entirely in that case rather than let it silently
    fail on click."""
    return _WINREG_AVAILABLE


def _launch_command(main_py_path: str) -> str:
    """Builds the command line the Run key will execute.

    Prefers pythonw.exe (no console window) over sys.executable, since
    sys.executable is python.exe (a visible console) when the app was
    launched via `python src/main.py` during development. If pythonw.exe
    isn't found alongside it, falls back to whatever launched this process.
    """
    python_exe = sys.executable
    pythonw_exe = python_exe.replace("python.exe", "pythonw.exe")
    exe_to_use = pythonw_exe if os.path.exists(pythonw_exe) else python_exe
    return f'"{exe_to_use}" "{main_py_path}"'


def is_startup_enabled() -> bool:
    """Reads the actual registry state (source of truth) rather than any
    locally cached flag, since the user could remove the entry manually
    via msconfig/Task Manager's Startup tab without the app knowing."""
    if not _WINREG_AVAILABLE:
        return False
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY_PATH, 0, winreg.KEY_READ) as key:
            winreg.QueryValueEx(key, APP_NAME)
            return True
    except OSError:
        return False


def enable_startup(main_py_path: str) -> bool:
    if not _WINREG_AVAILABLE:
        return False
    try:
        command = _launch_command(main_py_path)
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY_PATH, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, command)
        return True
    except OSError:
        return False


def disable_startup() -> bool:
    if not _WINREG_AVAILABLE:
        return False
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY_PATH, 0, winreg.KEY_SET_VALUE) as key:
            winreg.DeleteValue(key, APP_NAME)
        return True
    except FileNotFoundError:
        return True  # Already absent - not an error from the caller's view.
    except OSError:
        return False
