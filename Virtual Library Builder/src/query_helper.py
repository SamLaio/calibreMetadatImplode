"""A local, visual helper for native calibre search expressions."""
from qt.core import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton,
    QTableWidget, QHeaderView, QPlainTextEdit, QDialogButtonBox,
)
from calibre.gui2 import error_dialog
from calibre_plugins.virtual_library_builder import core
from calibre_plugins.virtual_library_builder.conditions import ConditionsTable


class QueryHelper(QDialog):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor
        self.metadata = editor.metadata
        self.setWindowTitle('進階條件產生器')
        self.resize(760, 440)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel('選欄位與條件來產生搜尋式；僅帶回編輯區，不會直接儲存虛擬書庫。'))
        self.table = ConditionsTable(self.metadata)
        layout.addWidget(self.table)
        add = QPushButton('＋新增條件')
        add.clicked.connect(self.table.add_row)
        layout.addWidget(add)
        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setMaximumHeight(70)
        layout.addWidget(self.output)
        self.join = QComboBox()
        for text, mode in [('與現有搜尋式全部符合（AND）', 'and'), ('與現有搜尋式任一符合（OR）', 'or'), ('取代整個搜尋式', 'replace')]:
            self.join.addItem(text, mode)
        layout.addWidget(self.join)
        self.status = QLabel()
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.apply_button = buttons.button(QDialogButtonBox.StandardButton.Ok)
        self.apply_button.setText('帶回搜尋式')
        buttons.accepted.connect(self.apply_expression)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.table.changed.connect(self.update_output)
        self.table.add_row()

    def generated(self):
        return self.table.generated()

    def update_output(self, *args):
        try:
            self.output.setPlainText(self.generated())
            self.status.setText('每列由上往下與前面結果做 AND／OR；相對日期會隨當日日期更新。')
            self.apply_button.setEnabled(True)
        except Exception as err:
            self.output.clear()
            self.status.setText(str(err))
            self.apply_button.setEnabled(False)

    def apply_expression(self):
        try:
            if self.editor.gui.current_db is not self.editor.db:
                raise ValueError('目前書庫已變更，請重新開啟建立器。')
            result = core.combine_search(self.editor.raw.toPlainText(), self.generated(), self.join.currentData())
            self.editor.db.new_api.search(result)
            self.editor.raw.setPlainText(result)
            self.accept()
        except Exception as err:
            error_dialog(self, '無法帶回搜尋式', str(err), show=True)
