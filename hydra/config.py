from __future__ import annotations

from pathlib import Path

APP_DIR = Path.home() / ".hydra"
PROFILES_DIR = APP_DIR / "profiles"
SESSIONS_FILE = APP_DIR / "sessions.json"
BACKUP_FILE = APP_DIR / "sessions.json.bak"
DEFAULT_LAYOUT = "2x2"
LAYOUTS = ("1x1", "1x2", "2x1", "2x2", "1x3", "3x1", "2x3", "3x2", "3x3")
DEFAULT_RELOAD_SECONDS = 30

COLORS = {
    "background": "#111318",
    "surface": "#181b21",
    "surface_alt": "#20242c",
    "surface_hover": "#272c35",
    "border": "#2e3440",
    "text": "#e6e9ef",
    "muted": "#8b93a1",
    "accent": "#7aa2f7",
    "accent_hover": "#8eafff",
    "danger": "#ef7b86",
    "success": "#77c89a",
}

QSS = f"""
QWidget {{
    background: {COLORS["background"]};
    color: {COLORS["text"]};
    font-family: "Segoe UI", "Ubuntu", sans-serif;
    font-size: 13px;
}}
QMainWindow {{ background: {COLORS["background"]}; }}
QFrame#sidebar, QFrame#pane {{
    background: {COLORS["surface"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 10px;
}}
QLabel#appTitle {{ font-size: 18px; font-weight: 700; }}
QLabel#sectionLabel {{
    color: {COLORS["muted"]};
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1px;
}}
QLabel#sessionTitle {{ font-size: 17px; font-weight: 700; }}
QLabel#paneTitle {{ font-size: 12px; font-weight: 700; }}
QLabel#paneMeta {{ color: {COLORS["muted"]}; font-size: 11px; }}
QLabel#status {{ color: {COLORS["muted"]}; font-size: 12px; }}
QPushButton, QToolButton {{
    background: {COLORS["surface_alt"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 7px;
    padding: 7px 10px;
}}
QPushButton:hover, QToolButton:hover {{ background: {COLORS["surface_hover"]}; }}
QPushButton:checked, QToolButton:checked {{
    background: {COLORS["accent"]};
    color: #0f1116;
    border-color: {COLORS["accent"]};
}}
QPushButton#primary {{
    background: {COLORS["accent"]};
    color: #0f1116;
    border-color: {COLORS["accent"]};
    font-weight: 700;
}}
QPushButton#primary:hover {{ background: {COLORS["accent_hover"]}; }}
QPushButton#danger {{ color: {COLORS["danger"]}; }}
QLineEdit, QComboBox, QSpinBox {{
    background: {COLORS["surface_alt"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 7px;
    padding: 6px 8px;
}}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus {{ border-color: {COLORS["accent"]}; }}
QListWidget {{ background: transparent; border: none; outline: none; }}
QListWidget::item {{
    background: {COLORS["surface_alt"]};
    border: 1px solid transparent;
    border-radius: 8px;
    padding: 10px;
    margin: 3px 0;
}}
QListWidget::item:hover {{ background: {COLORS["surface_hover"]}; }}
QListWidget::item:selected {{
    background: {COLORS["surface_hover"]};
    border-color: {COLORS["accent"]};
}}
QDialog {{ background: {COLORS["surface"]}; }}
QDialog QLabel {{ background: transparent; }}
QStatusBar {{ background: {COLORS["surface"]}; color: {COLORS["muted"]}; }}
QProgressBar {{
    background: {COLORS["surface_alt"]};
    border: none;
    border-radius: 3px;
    height: 4px;
}}
QProgressBar::chunk {{ background: {COLORS["accent"]}; border-radius: 3px; }}
"""
