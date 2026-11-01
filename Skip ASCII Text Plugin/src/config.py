try:
    from qt.core import (QCheckBox, QDialog, QDialogButtonBox, QFormLayout,
                         QGroupBox, QLabel, QVBoxLayout, QWidget)
except ImportError:
    from PyQt5.Qt import (QCheckBox, QDialog, QDialogButtonBox, QFormLayout,
                          QGroupBox, QLabel, QVBoxLayout, QWidget)

from calibre.utils.config import JSONConfig
from calibre_plugins.skip_ascii_text.icons import create_icon


prefs = JSONConfig('plugins/Skip Ascii Text Plugin')
prefs.defaults['SKIP_ASCII_TEXT'] = True


class ConfigWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        title = QLabel('中文檔名，保留原樣', self)
        font = title.font()
        font.setPointSizeF(font.pointSizeF() + 4)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)
        subtitle = QLabel('讓檔名中的中文保持原文，避免轉成拼音。', self)
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)
        self.enabled = QCheckBox('啟用原文字元保留', self)
        self.enabled.setChecked(prefs['SKIP_ASCII_TEXT'])
        layout.addWidget(self.enabled)
        self.status = QLabel(self)
        self.status.setWordWrap(True)
        self.enabled.toggled.connect(self.update_preview)
        layout.addWidget(self.status)
        example = QGroupBox('檔名效果示意', self)
        fields = QFormLayout(example)
        fields.setSpacing(12)
        fields.addRow('原始書名', QLabel('書店怪問', example))
        self.result = QLabel(example)
        fields.addRow('處理後', self.result)
        layout.addWidget(example)
        note = QLabel('按「儲存」後立即套用。既有檔名不會自動變更。', self)
        note.setWordWrap(True)
        layout.addWidget(note)
        layout.addStretch()
        self.setMinimumWidth(max(480, self.enabled.sizeHint().width() + 100,
                                 title.sizeHint().width() + 40))
        self.update_preview(self.enabled.isChecked())

    def update_preview(self, enabled):
        self.status.setText('將保留中文等原文字元。' if enabled else '將使用原本的檔名轉寫方式。')
        self.result.setText('書店怪問' if enabled else 'Shu Dian Guai Wen')

    def save_settings(self):
        prefs['SKIP_ASCII_TEXT'] = self.enabled.isChecked()


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('保留原文字元')
        self.setWindowIcon(create_icon())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 20)
        layout.setSpacing(20)
        self.settings = ConfigWidget()
        layout.addWidget(self.settings)
        self.buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel, self)
        self.buttons.button(QDialogButtonBox.Save).setText('儲存')
        self.buttons.button(QDialogButtonBox.Cancel).setText('取消')
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)
        self.adjustSize()
        self.setMinimumSize(self.sizeHint())
