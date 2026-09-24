from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QSpinBox,
)

from hydra.config import DEFAULT_LAYOUT, DEFAULT_RELOAD_SECONDS, LAYOUTS
from hydra.domain.models import PaneConfig, SessionConfig
from hydra.domain.validation import normalize_url, validate_layout, validate_profile_name


class PaneEditor(QDialog):
    def __init__(self, parent=None, config: PaneConfig | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Editar painel" if config else "Novo painel")
        self.setMinimumWidth(420)
        form = QFormLayout(self)

        self.name = QLineEdit(config.name if config else "")
        self.url = QLineEdit(config.url if config else "https://")
        self.profile = QLineEdit(config.profile if config else "")
        self.profile.setPlaceholderText("vazio para sessão anônima")
        self.reload = QSpinBox()
        self.reload.setRange(0, 86400)
        self.reload.setSuffix(" s")
        self.reload.setSpecialValueText("desligado")
        self.reload.setValue(config.auto_reload_s if config else 0)
        self.mute = QCheckBox("Silenciar áudio")
        self.mute.setChecked(config.mute if config else False)

        form.addRow("Nome", self.name)
        form.addRow("URL", self.url)
        form.addRow("Perfil", self.profile)
        form.addRow("Auto reload", self.reload)
        form.addRow("Áudio", self.mute)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def _accept(self) -> None:
        try:
            self.value()
        except ValueError as exc:
            QMessageBox.warning(self, "Valor inválido", str(exc))
            return
        self.accept()

    def value(self) -> PaneConfig:
        name = self.name.text().strip() or "Painel"
        return PaneConfig(
            name=name,
            url=normalize_url(self.url.text()),
            profile=validate_profile_name(self.profile.text()),
            auto_reload_s=self.reload.value(),
            mute=self.mute.isChecked(),
        )


class SessionEditor(QDialog):
    def __init__(self, parent=None, config: SessionConfig | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Editar sessão" if config else "Nova sessão")
        self.setMinimumWidth(380)
        form = QFormLayout(self)

        self.name = QLineEdit(config.name if config else "")
        self.layout = QComboBox()
        self.layout.addItems(LAYOUTS)
        self.layout.setCurrentText(config.layout if config else DEFAULT_LAYOUT)
        form.addRow("Nome", self.name)
        form.addRow("Layout", self.layout)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def _accept(self) -> None:
        try:
            self.value([])
        except ValueError as exc:
            QMessageBox.warning(self, "Valor inválido", str(exc))
            return
        self.accept()

    def value(self, panes: list[PaneConfig]) -> SessionConfig:
        name = self.name.text().strip() or "Sessão"
        return SessionConfig(
            name=name,
            layout=validate_layout(self.layout.currentText()),
            panes=panes,
        )
