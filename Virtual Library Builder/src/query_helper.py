"""A local, visual helper for native calibre search expressions."""
from qt.core import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton,
    QTableWidget, QHeaderView, QPlainTextEdit, QDialogButtonBox, Qt, QInputDialog,
)
from calibre.gui2 import error_dialog
from calibre_plugins.virtual_library_builder import core
from calibre_plugins.virtual_library_builder.conditions import ConditionsTable


class QueryHelper(QDialog):
    def __init__(self, editor=None, gui=None):
        super().__init__(editor if editor is not None else gui)
        if editor is None:
            self.setWindowFlags(Qt.WindowType.Window)
            self.setWindowModality(Qt.WindowModality.NonModal)
            self.setModal(False)
        self.editor = editor
        self.gui = editor.gui if editor is not None else gui
        self.db = self.gui.current_db
        self.metadata = core.fields(self.db)
        if editor is None:
            if not hasattr(self.gui, '_library_builder_filter_states'):
                self.gui._library_builder_filter_states = {}
            self.session_states = self.gui._library_builder_filter_states
            self.library_key = self.db.library_id
        self.original_search = self.gui.search.currentText() if editor is None else None
        self.last_applied_search = self.original_search
        self.setWindowTitle('條件篩選器' if editor is None else '進階條件產生器')
        self.resize(760, 440)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel('套用搜尋保留目前虛擬書庫範圍；也可按「建立書庫」另存目前組合條件。' if editor is None else '選欄位與條件來產生搜尋式；僅帶回編輯區，不會直接儲存虛擬書庫。'))
        self.table = ConditionsTable(self.metadata)
        layout.addWidget(self.table)
        add = QPushButton('＋新增條件')
        add.clicked.connect(self.table.add_row)
        condition_buttons = QHBoxLayout()
        condition_buttons.addWidget(add, 1)
        self.clear_button = QPushButton('清空條件')
        self.clear_button.clicked.connect(self.clear_conditions)
        condition_buttons.addWidget(self.clear_button)
        layout.addLayout(condition_buttons)
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
        self.apply_button.setText('套用搜尋' if editor is None else '帶回搜尋式')
        buttons.accepted.connect(self.apply_expression)
        if editor is None:
            buttons.button(QDialogButtonBox.StandardButton.Cancel).setText('關閉')
        buttons.rejected.connect(self.reject)
        bottom = QHBoxLayout()
        if editor is None:
            self.create_library_button = QPushButton('建立書庫')
            self.create_library_button.clicked.connect(self.create_library)
            bottom.addWidget(self.create_library_button)
        bottom.addStretch()
        bottom.addWidget(buttons)
        layout.addLayout(bottom)
        self.table.changed.connect(self.update_output)
        self.table.add_row()
        if editor is None:
            self.restore_filter_state()

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

    def composed_search(self):
        if self.gui.current_db is not self.db:
            raise ValueError('目前書庫已變更，請重新開啟。')
        if self.editor is None and self.gui.search.currentText() != self.last_applied_search:
            raise ValueError('搜尋列已變更，請重新開啟條件篩選器。')
        existing = self.original_search if self.editor is None else self.editor.raw.toPlainText()
        result = core.combine_search(existing, self.generated(), self.join.currentData())
        self.db.new_api.search(result)
        return result

    def create_library(self):
        try:
            search = self.composed_search()
            scope = (self.db.data.get_base_restriction(), self.db.data.get_search_restriction())
            expected = dict(self.db.new_api.pref('virtual_libraries', {}))
            name, accepted = QInputDialog.getText(self, '建立書庫', '虛擬書庫名稱（1～40 字）：')
            if not accepted:
                return
            name = name.strip()
            if self.composed_search() != search or scope != (self.db.data.get_base_restriction(), self.db.data.get_search_restriction()):
                raise ValueError('條件或虛擬書庫範圍已變更，請重試。')
            if name in expected:
                raise ValueError('名稱已存在，請換一個名稱；不會覆蓋既有書庫。')
            full_search = core.expression([term for term in (*scope, search) if term])
            rows = core.plan(self.db, [(name, full_search)])
            core.save(self.db, rows, expected)
            self.gui.library_view.model().refresh()
            self.gui.virtual_libraries_changed()
            self.save_filter_state()
            self.status.setText('已建立虛擬書庫「' + name + '」，目前搜尋與範圍保持不變。')
        except Exception as err:
            error_dialog(self, '無法建立書庫', str(err), show=True)

    def apply_expression(self):
        try:
            result = self.composed_search()
            if self.editor is None:
                self.gui.search.set_search_string(result)
                self.last_applied_search = self.gui.search.currentText()
                self.save_filter_state()
                self.status.setText('已套用搜尋，可繼續調整；關閉視窗會保留目前搜尋。')
            else:
                self.editor.raw.setPlainText(result)
                self.accept()
        except Exception as err:
            error_dialog(self, '無法套用搜尋' if self.editor is None else '無法帶回搜尋式', str(err), show=True)

    def save_filter_state(self):
        if self.editor is not None or self.gui.current_db is not self.db:
            return
        rows = []
        for row in range(self.table.rowCount()):
            field, op, value, join = [self.table.cellWidget(row, col) for col in range(4)]
            rows.append([field.currentData(), op.currentData(), value.text(), join.currentData()])
        self.session_states[self.library_key] = {
            'rows': rows, 'mode': self.join.currentData(),
            'base': self.original_search, 'last_applied': self.last_applied_search,
        }

    def restore_filter_state(self):
        state = self.session_states.get(self.library_key, {})
        if not isinstance(state, dict):
            return
        rows = state.get('rows')
        if not isinstance(rows, list):
            return
        self.table.setRowCount(0)
        for saved in rows:
            if not isinstance(saved, (list, tuple)) or len(saved) != 4:
                continue
            key, operator, value, join = saved
            if key not in self.metadata or not isinstance(value, str):
                continue
            self.table.add_row()
            row = self.table.rowCount() - 1
            field, op = [self.table.cellWidget(row, col) for col in range(2)]
            field.setCurrentIndex(field.findData(key))
            index = op.findData(operator)
            if index < 0:
                self.table.removeRow(row)
                continue
            op.setCurrentIndex(index)
            self.table.cellWidget(row, 2).setText(value)
            self.table.cellWidget(row, 3).setCurrentIndex(1 if join == 'or' else 0)
        if not self.table.rowCount():
            self.table.add_row()
        self.table.update_joins()
        mode = self.join.findData(state.get('mode', 'and'))
        self.join.setCurrentIndex(max(0, mode))
        if state.get('last_applied') == self.original_search:
            self.original_search = state.get('base', self.original_search)
        self.update_output()

    def clear_conditions(self):
        if self.gui.current_db is not self.db:
            error_dialog(self, '無法清空條件', '目前書庫已變更，請重新開啟。', show=True)
            return
        if self.editor is None:
            current = self.gui.search.currentText()
            if current == self.last_applied_search and current != self.original_search:
                self.gui.search.set_search_string(self.original_search)
            self.original_search = self.gui.search.currentText()
            self.last_applied_search = self.original_search
        self.table.setRowCount(0)
        self.table.add_row()
        self.join.setCurrentIndex(0)
        self.save_filter_state()
        self.status.setText('已清空條件；原有或手動改寫的搜尋保持不變。')

    def reject(self):
        self.save_filter_state()
        super().reject()

    def closeEvent(self, event):
        self.save_filter_state()
        super().closeEvent(event)
