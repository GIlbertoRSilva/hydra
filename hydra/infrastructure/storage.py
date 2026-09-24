from __future__ import annotations

import json
import os
from dataclasses import asdict
from pathlib import Path
from tempfile import NamedTemporaryFile

from hydra.domain.models import HydraState, PaneConfig, SessionConfig, default_session, new_id
from hydra.domain.validation import validate_profile_name


class SessionStore:
    def __init__(self, path: Path, backup_path: Path | None = None) -> None:
        self.path = path
        self.backup_path = backup_path or path.with_suffix(path.suffix + ".bak")

    def load(self) -> HydraState:
        data = self._read(self.path)
        if data is None and self.backup_path.exists():
            data = self._read(self.backup_path)
        if data is None:
            state = HydraState([default_session()])
            state.ensure_valid()
            return state
        if not isinstance(data, dict):
            state = HydraState([default_session()])
            state.ensure_valid()
            return state
        state = self._deserialize(data)
        state.ensure_valid()
        return state

    def save(self, state: HydraState) -> None:
        state.ensure_valid()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"version": 2, "active_session_id": state.active_session_id, "sessions": []}
        for session in state.sessions:
            payload["sessions"].append(asdict(session))
        serialized = json.dumps(payload, ensure_ascii=False, indent=2)
        with NamedTemporaryFile("w", encoding="utf-8", dir=self.path.parent, delete=False) as temp:
            temp.write(serialized)
            temp_path = Path(temp.name)
        if self.path.exists():
            self._copy(self.path, self.backup_path)
        os.replace(temp_path, self.path)

    @staticmethod
    def _copy(source: Path, target: Path) -> None:
        target.write_bytes(source.read_bytes())

    @staticmethod
    def _read(path: Path) -> dict | None:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, TypeError):
            return None

    @staticmethod
    def _deserialize(data: dict) -> HydraState:
        sessions: list[SessionConfig] = []
        for raw_session in data.get("sessions", []):
            if not isinstance(raw_session, dict):
                continue
            panes: list[PaneConfig] = []
            for raw_pane in raw_session.get("panes", []):
                if not isinstance(raw_pane, dict):
                    continue
                raw_profile = str(raw_pane.get("profile", "")).strip()
                try:
                    profile = validate_profile_name(raw_profile)
                except ValueError:
                    profile = ""
                panes.append(
                    PaneConfig(
                        name=str(raw_pane.get("name", "Painel")).strip() or "Painel",
                        url=str(raw_pane.get("url", "about:blank")).strip() or "about:blank",
                        profile=profile,
                        auto_reload_s=SessionStore._safe_int(raw_pane.get("auto_reload_s", 0)),
                        mute=SessionStore._safe_bool(raw_pane.get("mute", False)),
                        id=str(raw_pane.get("id", "")) or new_id(),
                    )
                )
            sessions.append(
                SessionConfig(
                    name=str(raw_session.get("name", "Sessão")).strip() or "Sessão",
                    layout=str(raw_session.get("layout", "2x2")),
                    panes=panes,
                    id=str(raw_session.get("id", "")) or new_id(),
                )
            )
        return HydraState(sessions=sessions, active_session_id=str(data.get("active_session_id", "")))

    @staticmethod
    def _safe_int(value: object) -> int:
        try:
            return max(0, int(value))
        except (TypeError, ValueError):
            return 0

    @staticmethod
    def _safe_bool(value: object) -> bool:
        if isinstance(value, bool):
            return value
        return str(value).strip().lower() in {"1", "true", "yes", "sim"}
