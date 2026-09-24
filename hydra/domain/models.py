from __future__ import annotations

from dataclasses import dataclass, field
from uuid import uuid4

from hydra.config import DEFAULT_LAYOUT, LAYOUTS


def new_id() -> str:
    return uuid4().hex


@dataclass(slots=True)
class PaneConfig:
    name: str
    url: str
    profile: str = ""
    auto_reload_s: int = 0
    mute: bool = False
    id: str = field(default_factory=new_id)

    def clone(self) -> "PaneConfig":
        return PaneConfig(
            name=self.name,
            url=self.url,
            profile=self.profile,
            auto_reload_s=self.auto_reload_s,
            mute=self.mute,
        )


@dataclass(slots=True)
class SessionConfig:
    name: str
    layout: str = DEFAULT_LAYOUT
    panes: list[PaneConfig] = field(default_factory=list)
    id: str = field(default_factory=new_id)

    def normalized_layout(self) -> str:
        return self.layout if self.layout in LAYOUTS else DEFAULT_LAYOUT


@dataclass(slots=True)
class HydraState:
    sessions: list[SessionConfig] = field(default_factory=list)
    active_session_id: str = ""

    def ensure_valid(self) -> None:
        if not self.sessions:
            self.sessions = [default_session()]
        session_ids = {session.id for session in self.sessions}
        if self.active_session_id not in session_ids:
            self.active_session_id = self.sessions[0].id
        for session in self.sessions:
            session.layout = session.normalized_layout()


def default_session() -> SessionConfig:
    return SessionConfig(
        name="Social",
        layout="2x3",
        panes=[
            PaneConfig("Facebook", "https://facebook.com", "conta_1"),
            PaneConfig("Instagram", "https://instagram.com", "conta_2"),
            PaneConfig("X", "https://x.com", "conta_3"),
            PaneConfig("YouTube 1", "https://youtube.com"),
            PaneConfig("YouTube 2", "https://youtube.com"),
        ],
    )
