from __future__ import annotations

import sys

import PySide6
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from PySide6.QtWebEngineCore import qWebEngineChromiumVersion

from hydra.application.session_manager import SessionManager
from hydra.config import QSS
from hydra.infrastructure.settings import AppPaths
from hydra.infrastructure.storage import SessionStore
from hydra.ui.window import HydraWindow
from hydra.web.profiles import ProfileManager


def build_window() -> HydraWindow:
    paths = AppPaths()
    paths.ensure()
    store = SessionStore(paths.sessions, paths.backup)
    manager = SessionManager(store.load(), store)
    profiles = ProfileManager(paths.profiles)
    return HydraWindow(manager, profiles)


def main() -> int:
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)
    app.setApplicationName("Hydra")
    app.setApplicationVersion("1.0.0")
    app.setStyleSheet(QSS)
    window = build_window()
    window.show()
    return app.exec()


def diagnostics() -> str:
    paths = AppPaths()
    paths.ensure()
    return "\n".join(
        [
            f"Python: {sys.version.split()[0]}",
            f"PySide6: {PySide6.__version__}",
            f"Chromium: {qWebEngineChromiumVersion()}",
            f"Diretório: {paths.root}",
            f"Perfis: {paths.profiles}",
            f"Sessões: {paths.sessions}",
        ]
    )
