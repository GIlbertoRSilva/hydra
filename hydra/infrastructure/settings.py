from __future__ import annotations

from pathlib import Path

from hydra.config import APP_DIR, BACKUP_FILE, PROFILES_DIR, SESSIONS_FILE


class AppPaths:
    def __init__(
        self,
        root: Path = APP_DIR,
        profiles: Path = PROFILES_DIR,
        sessions: Path = SESSIONS_FILE,
        backup: Path = BACKUP_FILE,
    ) -> None:
        self.root = root
        self.profiles = profiles
        self.sessions = sessions
        self.backup = backup

    def ensure(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.profiles.mkdir(parents=True, exist_ok=True)
