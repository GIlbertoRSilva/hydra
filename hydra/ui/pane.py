from __future__ import annotations

from PySide6.QtCore import QTimer, QUrl, Signal
from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QToolButton,
    QVBoxLayout,
)

from hydra.config import DEFAULT_RELOAD_SECONDS
from hydra.domain.models import PaneConfig
from hydra.domain.validation import normalize_url
from hydra.ui.dialogs import PaneEditor
from hydra.web.profiles import ProfileManager


class BrowserPane(QFrame):
    closed = Signal(object)
    changed = Signal()

    def __init__(self, config: PaneConfig, profiles: ProfileManager, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("pane")
        self.config = config
        self.profiles = profiles
        self._page: QWebEnginePage | None = None
        self._profile: QWebEngineProfile | None = None
        self._build_ui()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.reload)
        self._create_page()
        self._apply_config()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 6, 8, 8)
        root.setSpacing(6)

        header = QHBoxLayout()
        header.setSpacing(4)
        self.title = QLabel()
        self.title.setObjectName("paneTitle")
        self.meta = QLabel()
        self.meta.setObjectName("paneMeta")
        header.addWidget(self.title)
        header.addWidget(self.meta)
        header.addStretch()

        self.reload_button = self._tool("↻", "Recarregar")
        self.auto_button = self._tool("A", "Ativar ou desativar auto reload")
        self.auto_button.setCheckable(True)
        self.sound_button = self._tool("S", "Ativar ou silenciar áudio")
        self.sound_button.setCheckable(True)
        self.edit_button = self._tool("...", "Editar painel")
        self.close_button = self._tool("×", "Fechar painel")

        self.reload_button.clicked.connect(self.reload)
        self.auto_button.toggled.connect(self._toggle_auto)
        self.sound_button.toggled.connect(self._toggle_mute)
        self.edit_button.clicked.connect(self._edit)
        self.close_button.clicked.connect(lambda: self.closed.emit(self))

        for button in (
            self.reload_button,
            self.auto_button,
            self.sound_button,
            self.edit_button,
            self.close_button,
        ):
            header.addWidget(button)
        root.addLayout(header)

        self.url = QLineEdit()
        self.url.setPlaceholderText("Digite uma URL")
        self.url.returnPressed.connect(self._navigate)
        root.addWidget(self.url)

        self.view = QWebEngineView()
        self.view.setMinimumWidth(260)
        self.view.urlChanged.connect(self._url_changed)
        self.view.titleChanged.connect(self._page_title_changed)
        root.addWidget(self.view, 1)

    @staticmethod
    def _tool(text: str, tooltip: str) -> QToolButton:
        button = QToolButton()
        button.setText(text)
        button.setToolTip(tooltip)
        button.setAutoRaise(True)
        return button

    def _create_page(self) -> None:
        old_page = self._page
        self._page = None
        if old_page is not None:
            self.view.setPage(None)
            old_page.deleteLater()

        self._profile = self.profiles.get(self.config.profile, self)
        self._page = QWebEnginePage(self._profile, self)
        self._page.loadStarted.connect(self._load_started)
        self._page.loadFinished.connect(self._load_finished)
        self._page.newWindowRequested.connect(self._open_in_same_panel)
        self.view.setPage(self._page)

    def _apply_config(self) -> None:
        self.title.setText(self.config.name)
        self._update_meta()
        self.url.setText(self.config.url)
        self.sound_button.blockSignals(True)
        self.sound_button.setChecked(self.config.mute)
        self.sound_button.blockSignals(False)
        self._apply_mute()
        self.auto_button.blockSignals(True)
        self.auto_button.setChecked(self.config.auto_reload_s > 0)
        self.auto_button.blockSignals(False)
        self._apply_auto()
        self.view.setUrl(QUrl(self.config.url))

    def _update_meta(self) -> None:
        self.meta.setText(f"· {self.config.profile or 'anônimo'}")

    def _apply_mute(self) -> None:
        if self._page is not None:
            self._page.setAudioMuted(self.config.mute)
        self.sound_button.setToolTip("Ativar áudio" if self.config.mute else "Silenciar áudio")

    def _apply_auto(self) -> None:
        if self.config.auto_reload_s > 0:
            self._timer.start(self.config.auto_reload_s * 1000)
        else:
            self._timer.stop()

    def _toggle_auto(self, enabled: bool) -> None:
        self.config.auto_reload_s = DEFAULT_RELOAD_SECONDS if enabled else 0
        self._apply_auto()
        self.changed.emit()

    def _toggle_mute(self, enabled: bool) -> None:
        self.config.mute = enabled
        self._apply_mute()
        self.changed.emit()

    def _navigate(self) -> None:
        try:
            url = normalize_url(self.url.text())
        except ValueError:
            self.url.setText(self.config.url)
            return
        self.config.url = url
        self.view.setUrl(QUrl(url))
        self.changed.emit()

    def _url_changed(self, url: QUrl) -> None:
        if url.isValid() and url.toString():
            self.url.setText(url.toString())
            if url.scheme() in {"http", "https", "about"}:
                self.config.url = url.toString()
                self.changed.emit()

    def _page_title_changed(self, title: str) -> None:
        if title.strip():
            self.title.setToolTip(title.strip())

    def _open_in_same_panel(self, request) -> None:
        if self._page is not None:
            request.openIn(self._page)

    def _load_started(self) -> None:
        self.setProperty("loading", True)

    def _load_finished(self, ok: bool) -> None:
        self.setProperty("loading", False)
        self.status = "Carregado" if ok else "Falha ao carregar"

    def reload(self) -> None:
        self.view.reload()

    def edit_config(self, config: PaneConfig) -> None:
        profile_changed = config.profile != self.config.profile
        self.config.name = config.name
        self.config.url = config.url
        self.config.auto_reload_s = config.auto_reload_s
        self.config.mute = config.mute
        self.config.profile = config.profile
        if profile_changed:
            self._create_page()
        self._apply_config()
        self.changed.emit()

    def _edit(self) -> None:
        dialog = PaneEditor(self, self.config)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.edit_config(dialog.value())

    def run_js(self, script: str, callback=None) -> None:
        if self._page is not None:
            self._page.runJavaScript(script, 0, callback)

    def shutdown(self) -> None:
        self._timer.stop()
        if self._page is not None:
            self.view.setPage(None)
            self._page.deleteLater()
            self._page = None
