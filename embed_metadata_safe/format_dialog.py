from __future__ import annotations

from qt.core import QCheckBox, QDialog, QDialogButtonBox, QFrame, QLabel, QScrollArea, QVBoxLayout, QWidget

from calibre_plugins.embed_metadata_safe.i18n import build_texts


class FormatSelectionDialog(QDialog):
    def __init__(self, formats, parent=None):
        super().__init__(parent)
        self.texts = build_texts()
        self._checkboxes = []

        self.setWindowTitle(self.texts.format_dialog_title)

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        body = QLabel(self.texts.format_dialog_body)
        body.setWordWrap(True)
        root.addWidget(body)

        if not formats:
            empty = QLabel(self.texts.format_dialog_empty)
            empty.setWordWrap(True)
            root.addWidget(empty)
        else:
            container = QWidget(self)
            container_layout = QVBoxLayout(container)
            container_layout.setContentsMargins(0, 0, 0, 0)
            container_layout.setSpacing(6)

            for fmt in sorted({fmt.upper() for fmt in formats}):
                checkbox = QCheckBox(fmt)
                checkbox.setChecked(True)
                checkbox.stateChanged.connect(self._update_ok_state)
                self._checkboxes.append(checkbox)
                container_layout.addWidget(checkbox)

            container_layout.addStretch(1)

            scroll = QScrollArea(self)
            scroll.setWidgetResizable(True)
            scroll.setFrameShape(QFrame.Shape.NoFrame)
            scroll.setWidget(container)
            root.addWidget(scroll)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, self)
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)
        self._ok_button = buttons.button(QDialogButtonBox.StandardButton.Ok)

        if not formats:
            self._ok_button.setEnabled(False)
        else:
            self._update_ok_state()

        self.resize(360, 320)

    def _update_ok_state(self, *_args):
        if not self._checkboxes:
            self._ok_button.setEnabled(False)
            return
        self._ok_button.setEnabled(any(cb.isChecked() for cb in self._checkboxes))

    def _accept(self):
        if not self.selected_formats():
            return
        self.accept()

    def selected_formats(self):
        return [cb.text().lower() for cb in self._checkboxes if cb.isChecked()]
