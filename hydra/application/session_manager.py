from __future__ import annotations

from hydra.domain.models import HydraState, PaneConfig, SessionConfig
from hydra.infrastructure.storage import SessionStore


class SessionManager:
    def __init__(self, state: HydraState, store: SessionStore) -> None:
        self.state = state
        self.store = store
        self.state.ensure_valid()

    @property
    def current(self) -> SessionConfig:
        for session in self.state.sessions:
            if session.id == self.state.active_session_id:
                return session
        self.state.active_session_id = self.state.sessions[0].id
        return self.state.sessions[0]

    def activate(self, session_id: str) -> SessionConfig:
        if session_id not in {session.id for session in self.state.sessions}:
            raise ValueError("Sessão inexistente.")
        self.state.active_session_id = session_id
        self.save()
        return self.current

    def add_session(self, session: SessionConfig) -> SessionConfig:
        self.state.sessions.append(session)
        self.state.active_session_id = session.id
        self.save()
        return session

    def update_session(self, session: SessionConfig) -> None:
        for index, current in enumerate(self.state.sessions):
            if current.id == session.id:
                self.state.sessions[index] = session
                self.save()
                return
        raise ValueError("Sessão inexistente.")

    def delete_session(self, session_id: str) -> None:
        if len(self.state.sessions) <= 1:
            raise ValueError("O Hydra precisa manter pelo menos uma sessão.")
        self.state.sessions = [s for s in self.state.sessions if s.id != session_id]
        if self.state.active_session_id == session_id:
            self.state.active_session_id = self.state.sessions[0].id
        self.save()

    def replace_current_panes(self, panes: list[PaneConfig]) -> None:
        self.current.panes = panes
        self.save()

    def update_current_layout(self, layout: str) -> None:
        self.current.layout = layout
        self.save()

    def save(self) -> None:
        self.store.save(self.state)
