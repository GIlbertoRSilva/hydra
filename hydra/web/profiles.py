from __future__ import annotations

import hashlib
from pathlib import Path

from PySide6.QtCore import QObject
from PySide6.QtWebEngineCore import QWebEngineProfile


class ProfileManager(QObject):
    def __init__(self, root: Path, parent=None) -> None:
        super().__init__(parent)
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)
        self._persistent: dict[str, QWebEngineProfile] = {}

    def get(self, profile_name: str, parent=None) -> QWebEngineProfile:
        profile_name = profile_name.strip()
        if not profile_name:
            return QWebEngineProfile(parent)
        if profile_name in self._persistent:
            return self._persistent[profile_name]

        storage_dir = self.root / profile_name
        storage_dir.mkdir(parents=True, exist_ok=True)
        profile = QWebEngineProfile(self._storage_name(profile_name), self)
        profile.setPersistentStoragePath(str(storage_dir))
        profile.setCachePath(str(storage_dir / "cache"))
        profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies)
        self._persistent[profile_name] = profile
        return profile

    def close(self) -> None:
        profiles = list(self._persistent.values())
        self._persistent.clear()
        for profile in profiles:
            profile.deleteLater()

    @staticmethod
    def _storage_name(profile_name: str) -> str:
        digest = hashlib.sha256(profile_name.encode("utf-8")).hexdigest()[:12]
        return f"hydra_{digest}"
