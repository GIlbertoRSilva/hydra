from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from hydra.application.session_manager import SessionManager
from hydra.config import LAYOUTS
from hydra.domain.models import PaneConfig, SessionConfig
from hydra.ui.dialogs import PaneEditor, SessionEditor
from hydra.ui.pane import BrowserPane
from hydra.web.profiles import ProfileManager


class HydraWindow(QMainWindow):
    def __init__(self, sessions: SessionManager, profiles: ProfileManager) -> None:
        super().__init__()
        self.manager = sessions
        self.profiles = profiles
        self.panes: list[BrowserPane] = []
        self._switching_session = False
        self.setWindowTitle("Hydra")
        self.resize(1500, 920)
        self._build_ui()
        self._setup_shortcuts()
        self._refresh_sidebar()
        self._load_current_session()

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)

        sidebar = self._build_sidebar()
        root.addWidget(sidebar)

        main = QWidget()
        main_layout = QVBoxLayout(main)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(10)

        top = QHBoxLayout()
        self.session_title = QLabel()
        self.session_title.setObjectName("sessionTitle")
        top.addWidget(self.session_title)
        top.addStretch()
        top.addWidget(QLabel("Layout"))
        self.layout_combo = QComboBox()
        self.layout_combo.addItems(LAYOUTS)
        self.layout_combo.currentTextChanged.connect(self._layout_changed)
        top.addWidget(self.layout_combo)
        add_pane = QPushButton("Adicionar painel")
        add_pane.setObjectName("primary")
        add_pane.clicked.connect(self._add_pane)
        top.addWidget(add_pane)
        main_layout.addLayout(top)

        self.grid_host = QWidget()
        self.grid = QGridLayout(self.grid_host)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setSpacing(8)
        main_layout.addWidget(self.grid_host, 1)

        root.addWidget(main, 1)
        self.status_label = QLabel()
        self.status_label.setObjectName("status")
        self.statusBar().addPermanentWidget(self.status_label)

    def _build_sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(250)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(8)

        title = QLabel("Hydra")
        title.setObjectName("appTitle")
        subtitle = QLabel("Navegadores por perfil")
        subtitle.setObjectName("paneMeta")
        section = QLabel("SESSÕES")
        section.setObjectName("sectionLabel")

        self.session_list = QListWidget()
        self.session_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.session_list.currentItemChanged.connect(self._session_selected)

        new_session = QPushButton("Nova sessão")
        new_session.setObjectName("primary")
        new_session.clicked.connect(self._new_session)
        rename = QPushButton("Renomear")
        rename.clicked.connect(self._rename_session)
        duplicate = QPushButton("Duplicar")
        duplicate.clicked.connect(self._duplicate_session)
        delete = QPushButton("Excluir")
        delete.setObjectName("danger")
        delete.clicked.connect(self._delete_session)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(8)
        layout.addWidget(section)
        layout.addWidget(self.session_list, 1)
        layout.addWidget(new_session)

        actions = QHBoxLayout()
        actions.setSpacing(4)
        actions.addWidget(rename)
        actions.addWidget(duplicate)
        actions.addWidget(delete)
        layout.addLayout(actions)
        return sidebar

    def _setup_shortcuts(self) -> None:
        for index in range(1, 10):
            action = QAction(self)
            action.setShortcut(QKeySequence(f"Ctrl+{index}"))
            action.triggered.connect(lambda _checked=False, i=index - 1: self._activate_by_index(i))
            self.addAction(action)

    def _activate_by_index(self, index: int) -> None:
        if 0 <= index < len(self.manager.state.sessions):
            self.session_list.setCurrentRow(index)

    def _refresh_sidebar(self) -> None:
        current_id = self.manager.current.id
        self.session_list.blockSignals(True)
        self.session_list.clear()
        target_row = 0
        for index, session in enumerate(self.manager.state.sessions):
            item = QListWidgetItem(f"{session.name}\n{len(session.panes)} painéis · {session.layout}")
            item.setData(Qt.ItemDataRole.UserRole, session.id)
            self.session_list.addItem(item)
            if session.id == current_id:
                target_row = index
        self.session_list.setCurrentRow(target_row)
        self.session_list.blockSignals(False)

    def _session_selected(self, current: QListWidgetItem | None, _previous: QListWidgetItem | None) -> None:
        if current is None:
            return
        session_id = current.data(Qt.ItemDataRole.UserRole)
        if session_id == self.manager.current.id or self._switching_session:
            return
        self._switch_session(session_id)

    def _switch_session(self, session_id: str) -> None:
        self._sync_current()
        self.manager.activate(session_id)
        self._load_current_session()

    def _load_current_session(self) -> None:
        session = self.manager.current
        self._switching_session = True
        try:
            self._destroy_panes()
            self.session_title.setText(session.name)
            self.layout_combo.blockSignals(True)
            self.layout_combo.setCurrentText(session.layout)
            self.layout_combo.blockSignals(False)
            for config in session.panes:
                self._spawn_pane(config)
            self._fit_layout_to_panes()
            self._rebuild_grid()
            self._refresh_status()
            self._refresh_sidebar()
        finally:
            self._switching_session = False

    def _spawn_pane(self, config: PaneConfig) -> None:
        pane = BrowserPane(config, self.profiles, self)
        pane.closed.connect(self._close_pane)
        pane.changed.connect(self._sync_current)
        self.panes.append(pane)

    def _destroy_panes(self) -> None:
        for pane in self.panes:
            pane.shutdown()
            pane.deleteLater()
        self.panes.clear()

    def _sync_current(self) -> None:
        if self._switching_session:
            return
        self.manager.replace_current_panes([pane.config for pane in self.panes])
        self._refresh_sidebar()
        self._refresh_status()

    def _layout_changed(self, layout: str) -> None:
        if self._switching_session:
            return
        self.manager.update_current_layout(layout)
        self._rebuild_grid()
        self._refresh_sidebar()
        self._refresh_status()

    def _rebuild_grid(self) -> None:
        while self.grid.count():
            item = self.grid.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(self.grid_host)

        rows, columns = map(int, self.layout_combo.currentText().split("x"))
        for index, pane in enumerate(self.panes):
            row, column = divmod(index, columns)
            if row < rows:
                self.grid.addWidget(pane, row, column)

        for row in range(rows):
            self.grid.setRowStretch(row, 1)
        for column in range(columns):
            self.grid.setColumnStretch(column, 1)

    def _refresh_status(self) -> None:
        profiles = {pane.config.profile for pane in self.panes if pane.config.profile}
        self.status_label.setText(f"{len(self.panes)} painéis · {len(profiles)} perfis persistentes")

    def _add_pane(self) -> None:
        dialog = PaneEditor(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._spawn_pane(dialog.value())
            self._fit_layout_to_panes()
            self._rebuild_grid()
            self._sync_current()

    def _fit_layout_to_panes(self) -> None:
        rows, columns = map(int, self.layout_combo.currentText().split("x"))
        if len(self.panes) <= rows * columns:
            return
        for layout in LAYOUTS:
            target_rows, target_columns = map(int, layout.split("x"))
            if len(self.panes) <= target_rows * target_columns:
                self.layout_combo.setCurrentText(layout)
                self.manager.update_current_layout(layout)
                return

    def _close_pane(self, pane: BrowserPane) -> None:
        if pane not in self.panes:
            return
        self.panes.remove(pane)
        pane.shutdown()
        pane.deleteLater()
        self._rebuild_grid()
        self._sync_current()

    def _new_session(self) -> None:
        dialog = SessionEditor(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            session = dialog.value([])
            self.manager.add_session(session)
            self._load_current_session()

    def _rename_session(self) -> None:
        session = self.manager.current
        dialog = SessionEditor(self, session)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated = dialog.value([pane.config for pane in self.panes])
            updated.id = session.id
            self.manager.update_session(updated)
            self._load_current_session()

    def _duplicate_session(self) -> None:
        source = self.manager.current
        clone = SessionConfig(
            name=f"{source.name} (cópia)",
            layout=source.layout,
            panes=[pane.clone() for pane in source.panes],
        )
        self.manager.add_session(clone)
        self._load_current_session()

    def _delete_session(self) -> None:
        session = self.manager.current
        if len(self.manager.state.sessions) <= 1:
            QMessageBox.information(self, "Sessão", "Mantenha pelo menos uma sessão.")
            return
        answer = QMessageBox.question(self, "Excluir sessão", f"Excluir a sessão \"{session.name}\"?")
        if answer != QMessageBox.StandardButton.Yes:
            return
        self._destroy_panes()
        self.manager.delete_session(session.id)
        self._load_current_session()

    def _sync_before_close(self) -> None:
        self._sync_current()
        self.manager.save()

    def closeEvent(self, event) -> None:
        self._sync_before_close()
        self._destroy_panes()
        self.profiles.close()
        event.accept()
