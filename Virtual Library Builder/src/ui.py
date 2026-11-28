from html import escape

from qt.core import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox, QTabWidget, QWidget,
    QPlainTextEdit, Qt, QIcon, QPixmap, QAbstractItemView, QListWidget, QListWidgetItem, QStackedWidget,
)
from calibre.gui2 import error_dialog, info_dialog, question_dialog
from calibre.gui2.actions import InterfaceAction
from calibre_plugins.virtual_library_builder import core
from calibre_plugins.virtual_library_builder.conditions import ConditionsTable


class BuilderAction(InterfaceAction):
    name = 'Virtual Library Builder'
    action_spec = ('書庫建立器', None, '依條件或欄位值建立虛擬書庫', ())
    action_type = 'current'

    def genesis(self):
        pixmap = QPixmap()
        pixmap.loadFromData(self.load_resources(['images/icon.png'])['images/icon.png'])
        self.qaction.setIcon(QIcon(pixmap))
        self.qaction.triggered.connect(self.show_builder)

    def show_builder(self):
        if self.gui.current_view() is not self.gui.library_view:
            return info_dialog(self.gui, '書庫建立器', '請先切回書庫。', show=True)
        BuilderDialog(self.gui).exec()


class BuilderDialog(QDialog):
    def __init__(self, gui):
        super().__init__(gui)
        self.gui = gui
        self.db = gui.current_db
        self.metadata = core.fields(self.db)
        self.rows = []
        self.editing = None
        self.loaded_search = None
        self.setWindowTitle('書庫建立器 0.1.6')
        action = getattr(gui, 'iactions', {}).get('Virtual Library Builder')
        if action is not None:
            self.setWindowIcon(action.qaction.icon())
        self.resize(1000, 840)
        layout = QVBoxLayout(self)
        label = QLabel('以整個實體書庫預覽，符合條件的新書會自動收錄；不搬動書籍。')
        label.setWordWrap(True)
        layout.addWidget(label)
        self.tabs = QTabWidget()
        content = QHBoxLayout()
        self.libraries = QListWidget()
        self.libraries.setMaximumWidth(210)
        self.libraries.setAccessibleName('選擇要修改的虛擬書庫')
        library_pane = QWidget()
        library_layout = QVBoxLayout(library_pane)
        library_layout.setContentsMargins(0, 0, 0, 0)
        library_layout.addWidget(self.libraries)
        moves = QHBoxLayout()
        self.move_up = QPushButton('↑ 上移')
        self.move_down = QPushButton('↓ 下移')
        for button, delta in ((self.move_up, -1), (self.move_down, 1)):
            button.setToolTip('排列立即保存，並同步原生虛擬書庫分頁')
            button.clicked.connect(lambda unused=False, delta=delta: self.move_library(delta))
            moves.addWidget(button)
        library_layout.addLayout(moves)
        library_layout.addWidget(QLabel('排列立即保存'))
        self.libraries.currentRowChanged.connect(self.update_move_buttons)
        self.delete = QPushButton('刪除所選虛擬書庫')
        self.delete.setEnabled(False)
        self.delete.clicked.connect(self.delete_library)
        library_layout.addWidget(self.delete)
        content.addWidget(library_pane)
        content.addWidget(self.tabs, 1)
        layout.addLayout(content, 1)
        single = QWidget()
        sl = QVBoxLayout(single)
        self.name = QLineEdit()
        self.name.setMaxLength(40)
        self.name.setPlaceholderText('虛擬書庫名稱（最多 40 字）')
        self.name.setAccessibleName('虛擬書庫名稱')
        sl.addWidget(self.name)
        self.advanced = QCheckBox('進階編輯條件（搜尋式）')
        self.advanced.toggled.connect(self.toggle_advanced)
        sl.addWidget(self.advanced)
        self.editor_stack = QStackedWidget()
        self.editor_stack.setMinimumHeight(340)
        sl.addWidget(self.editor_stack, 1)
        basic_page = QWidget()
        basic_layout = QVBoxLayout(basic_page)
        basic_layout.setContentsMargins(0, 0, 0, 0)
        advanced_page = QWidget()
        advanced_layout = QVBoxLayout(advanced_page)
        advanced_layout.setContentsMargins(0, 0, 0, 0)
        self.editor_stack.addWidget(basic_page)
        self.editor_stack.addWidget(advanced_page)
        self.conditions = ConditionsTable(self.metadata)
        basic_layout.addWidget(QLabel('由上往下組合：每列的 AND／OR 套用到前面全部結果；第一列不需選擇。'))
        basic_layout.addWidget(self.conditions, 1)
        self.form_search = QPlainTextEdit()
        self.form_search.setReadOnly(True)
        self.form_search.setMaximumHeight(60)
        self.form_search.setPlaceholderText('產生的搜尋式')
        self.conditions.changed.connect(self.update_form_search)
        basic_layout.addWidget(self.form_search)
        add = QPushButton('＋新增條件')
        add.clicked.connect(self.add_condition)
        basic_layout.addWidget(add)
        self.raw = QPlainTextEdit()
        self.raw.setAccessibleName('原始搜尋條件')
        self.raw.setPlaceholderText('原始搜尋條件')
        advanced_layout.addWidget(self.raw, 1)
        self.raw_note = QLabel('直接編輯 calibre 搜尋式，可使用 and、or、not 與括號；儲存前會檢查語法。')
        self.raw_note.setWordWrap(True)
        raw_footer = QHBoxLayout()
        raw_footer.addWidget(self.raw_note, 1)
        self.query_helper = QPushButton('條件產生器…')
        self.query_helper.clicked.connect(self.open_query_helper)
        raw_footer.addWidget(self.query_helper)
        advanced_layout.addLayout(raw_footer)
        self.add_button = add
        self.tabs.addTab(single, '條件建立')
        batch = QWidget()
        bl = QVBoxLayout(batch)
        self.batch_field = self.field_combo(batch=True)
        bl.addWidget(self.batch_field)
        self.template = QLineEdit('{欄位}－{值}')
        self.template.setAccessibleName('批次名稱範本')
        bl.addWidget(QLabel('名稱範本：可用 {欄位} 與 {值}'))
        bl.addWidget(self.template)
        self.filter = QLineEdit()
        self.filter.setPlaceholderText('搜尋欄位值…')
        self.filter.setClearButtonEnabled(True)
        bl.addWidget(self.filter)
        self.values = QTableWidget(0, 2)
        self.values.setHorizontalHeaderLabels(['勾選要建立的值', '本數'])
        self.values.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        bl.addWidget(self.values)
        buttons = QHBoxLayout()
        for text, checked in [('勾選可見項目', True), ('取消全部勾選', False)]:
            button = QPushButton(text)
            button.clicked.connect(lambda unused=False, checked=checked: self.check_values(checked))
            buttons.addWidget(button)
        bl.addLayout(buttons)
        self.tabs.addTab(batch, '依欄位批次建立')
        self.conflict = QComboBox()
        self.conflict.addItems(['同名：跳過', '同名：自動加序號', '同名：更新條件（需確認）'])
        layout.addWidget(self.conflict)
        self.conflict.hide()
        self.tabs.setTabVisible(1, False)
        self.tabs.tabBar().hide()
        self.batch_toggle = QPushButton('批次建立…')
        self.batch_toggle.clicked.connect(self.toggle_batch)
        layout.addWidget(self.batch_toggle)
        self.tabs.currentChanged.connect(lambda index: self.conflict.setVisible(index == 1))
        preview = QPushButton('預覽結果（不儲存）')
        preview.clicked.connect(self.preview)
        layout.addWidget(preview)
        self.summary = QLabel('尚未預覽。修改條件後請重新預覽。')
        layout.addWidget(self.summary)
        self.results = QTableWidget(0, 4)
        self.results.setHorizontalHeaderLabels(['名稱', '本數', '動作', '搜尋條件'])
        self.results.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.results.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.results.hide()
        self.details = QCheckBox('顯示搜尋條件與處理明細')
        self.details.toggled.connect(self.results.setVisible)
        layout.addWidget(self.details)
        layout.addWidget(self.results)
        self.books = QPlainTextEdit()
        self.books.setReadOnly(True)
        self.books.setPlaceholderText('預覽書目（最多 50 本）')
        self.books.setMaximumHeight(110)
        layout.addWidget(self.books)
        self.activate = QCheckBox('儲存後切換到書庫')
        layout.addWidget(self.activate)
        bottom = QHBoxLayout()
        bottom.addStretch()
        cancel = QPushButton('取消')
        cancel.clicked.connect(self.reject)
        self.create = QPushButton('建立虛擬書庫')
        self.create.setEnabled(True)
        self.create.clicked.connect(self.create_libraries)
        bottom.addWidget(cancel)
        bottom.addWidget(self.create)
        layout.addLayout(bottom)
        self.batch_field.currentIndexChanged.connect(self.load_values)
        self.filter.textChanged.connect(self.filter_values)
        self.add_condition()
        self.load_values()
        self.refresh_libraries()
        self.libraries.currentItemChanged.connect(self.select_library)
        self.loaded_draft = self.draft_state()

    def refresh_libraries(self):
        self.libraries.blockSignals(True)
        self.libraries.clear()
        item = QListWidgetItem('＋新增虛擬書庫')
        item.setData(Qt.ItemDataRole.UserRole, None)
        self.libraries.addItem(item)
        for name in core.ordered_names(self.db):
            item = QListWidgetItem(name)
            item.setData(Qt.ItemDataRole.UserRole, name)
            self.libraries.addItem(item)
        self.libraries.setCurrentRow(0)
        self.libraries.blockSignals(False)
        self.update_move_buttons()

    def toggle_batch(self):
        batch = self.tabs.currentIndex() == 0
        self.tabs.setTabVisible(1, batch)
        self.tabs.setCurrentIndex(1 if batch else 0)
        self.batch_toggle.setText('返回單一書庫' if batch else '批次建立…')
        self.libraries.setEnabled(not batch)
        self.delete.setEnabled(not batch and self.editing is not None)
        self.update_move_buttons()
        self.create.setText('批次建立' if batch else '儲存修改' if self.editing else '建立虛擬書庫')

    def update_move_buttons(self, *args):
        row = self.libraries.currentRow()
        single = self.tabs.currentIndex() == 0
        self.move_up.setEnabled(single and row > 1)
        self.move_down.setEnabled(single and 0 < row < self.libraries.count() - 1)

    def move_library(self, delta):
        row = self.libraries.currentRow()
        target = row + delta
        if self.tabs.currentIndex() != 0 or row < 1 or target < 1 or target >= self.libraries.count():
            return
        try:
            if self.gui.current_db is not self.db:
                raise ValueError('目前書庫已變更，請重新開啟。')
            expected = [self.libraries.item(i).data(Qt.ItemDataRole.UserRole) for i in range(1, self.libraries.count())]
            names = list(expected)
            names[row - 1], names[target - 1] = names[target - 1], names[row - 1]
            core.save_order(self.db, names, expected)
            # Keep the editor and its unsaved draft intact while moving the same item.
            self.libraries.blockSignals(True)
            item = self.libraries.takeItem(row)
            self.libraries.insertItem(target, item)
            self.libraries.setCurrentItem(item)
            self.libraries.blockSignals(False)
            self.update_move_buttons()
            self.gui.rebuild_vl_tabs()
        except Exception as err:
            error_dialog(self, '無法移動虛擬書庫', str(err), show=True)

    def select_library(self, item, previous=None):
        if item is None:
            return
        # A switch never writes the draft. Ask before discarding changed inputs.
        if hasattr(self, 'loaded_draft') and self.draft_state() != self.loaded_draft:
            if not question_dialog(self, '切換書庫', '放棄目前尚未儲存的修改？', default_yes=False):
                self.libraries.blockSignals(True)
                self.libraries.setCurrentItem(previous)
                self.libraries.blockSignals(False)
                self.update_move_buttons()
                return
        self.editing = item.data(Qt.ItemDataRole.UserRole)
        self.loaded_search = self.db.new_api.pref('virtual_libraries', {}).get(self.editing)
        self.name.setText(self.editing or '')
        self.name.setReadOnly(False)
        parsed = core.editable_rows(self.loaded_search, self.metadata) if self.editing else []
        if parsed is None:
            self.raw.setPlainText(self.loaded_search)
        else:
            self.populate_conditions(parsed)
            self.raw.clear()
        self.set_editor_mode(parsed is None)
        self.delete.setEnabled(self.editing is not None)
        self.create.setText('儲存修改' if self.editing else '建立虛擬書庫')
        self.create.setEnabled(True)
        self.books.clear()
        self.results.setRowCount(0)
        self.summary.setText('修改條件後可先查看符合書籍，或直接儲存。')
        self.loaded_draft = self.draft_state()

    def populate_conditions(self, parsed):
        self.conditions.setRowCount(0)
        rows = parsed
        for key, op, value, join in rows:
            self.add_condition()
            row = self.conditions.rowCount() - 1
            field = self.conditions.cellWidget(row, 0)
            field.setCurrentIndex(field.findData(key))
            operator = self.conditions.cellWidget(row, 1)
            operator.setCurrentIndex(operator.findData(op))
            self.conditions.cellWidget(row, 2).setText(value)
            self.conditions.cellWidget(row, 3).setCurrentIndex(1 if join == 'or' else 0)
        if not rows:
            self.add_condition()

    def set_editor_mode(self, advanced):
        self.raw_mode = advanced
        self.advanced.blockSignals(True)
        self.advanced.setChecked(advanced)
        self.advanced.blockSignals(False)
        self.editor_stack.setCurrentIndex(1 if advanced else 0)

    def open_query_helper(self):
        from calibre_plugins.virtual_library_builder.query_helper import QueryHelper
        QueryHelper(self).exec()

    def toggle_advanced(self, advanced):
        if advanced:
            try:
                search = self.inputs()[0][0][1]
            except ValueError as err:
                empty = all(not self.conditions.cellWidget(row, 2).text().strip()
                            for row in range(self.conditions.rowCount()))
                if self.editing or not empty:
                    self.set_editor_mode(False)
                    error_dialog(self, '無法轉換條件', str(err), show=True)
                    return
                search = ''
            self.raw.setPlainText(search)
        else:
            parsed = core.editable_rows(self.raw.toPlainText().strip(), self.metadata)
            if parsed is None:
                self.set_editor_mode(True)
                info_dialog(self, '保留進階編輯', '目前搜尋式無法完整轉成簡易條件，請繼續使用進階編輯。原式保持不變。', show=True)
                return
            self.populate_conditions(parsed)
        self.set_editor_mode(advanced)

    def delete_library(self):
        name = self.editing
        if name is None or self.tabs.currentIndex() != 0:
            return
        try:
            def check_current():
                if self.gui.current_db is not self.db:
                    raise ValueError('目前書庫已變更，請重新開啟建立器。')
                libraries = self.db.new_api.pref('virtual_libraries', {})
                if name not in libraries or libraries[name] != self.loaded_search:
                    raise ValueError('所選虛擬書庫已變更，請重新開啟後再刪除。')
            check_current()
            if not question_dialog(self, '刪除虛擬書庫',
                                   f'確定刪除「{escape(name)}」？只移除虛擬書庫設定，不會刪除書籍。尚未儲存的修改也會放棄。', default_yes=False):
                return
            check_current()
            self.gui._remove_vl(name, reapply=True)
            self.db.new_api.clear_search_caches()
            self.gui.library_view.model().refresh()
            self.gui.virtual_libraries_changed()
            self.refresh_libraries()
            if hasattr(self, 'loaded_draft'):
                del self.loaded_draft
            self.select_library(self.libraries.currentItem())
            self.summary.setText('已刪除虛擬書庫「' + name + '」，書籍保留。')
        except Exception as err:
            error_dialog(self, '無法刪除虛擬書庫', str(err), show=True)

    def draft_state(self):
        rows = tuple(tuple(self.conditions.cellWidget(row, col).currentData() if col < 2 else self.conditions.cellWidget(row, col).text()
                           for col in range(3)) for row in range(self.conditions.rowCount()))
        joins = tuple(self.conditions.cellWidget(row, 3).currentData() for row in range(self.conditions.rowCount()))
        return self.name.text(), joins, rows, self.raw.toPlainText(), getattr(self, 'raw_mode', False)

    def field_combo(self, batch=False):
        combo = QComboBox()
        for key, meta in self.metadata.items():
            if not batch or meta['datatype'] in {'text', 'series', 'enumeration'}:
                combo.addItem(str(meta.get('name') or key) + ' (' + key + ')', key)
        index = combo.findData('tags')
        if index >= 0:
            combo.setCurrentIndex(index)
        return combo

    def add_condition(self):
        self.conditions.add_row()

    def update_form_search(self):
        try:
            self.form_search.setPlainText(self.conditions.generated())
        except Exception as err:
            self.form_search.setPlainText(str(err))

    def load_values(self):
        try:
            entries = core.batch_values(self.db, self.batch_field.currentData())
            self.values.setRowCount(len(entries))
            for row, (term, count) in enumerate(entries):
                item = QTableWidgetItem(term)
                item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(Qt.CheckState.Unchecked)
                self.values.setItem(row, 0, item)
                count_item = QTableWidgetItem(str(count))
                count_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
                self.values.setItem(row, 1, count_item)
            self.filter_values()
        except Exception as err:
            self.summary.setText(str(err))

    def filter_values(self):
        text = self.filter.text().casefold()
        for row in range(self.values.rowCount()):
            self.values.setRowHidden(row, text not in self.values.item(row, 0).text().casefold())

    def check_values(self, checked):
        for row in range(self.values.rowCount()):
            if not checked or not self.values.isRowHidden(row):
                self.values.item(row, 0).setCheckState(Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked)

    def inputs(self):
        if self.gui.current_db is not self.db:
            raise ValueError('目前書庫已變更，請關閉後重新開啟建立器。')
        if self.tabs.currentIndex() == 0:
            if self.editing and self.db.new_api.pref('virtual_libraries', {}).get(self.editing) != self.loaded_search:
                raise ValueError('此書庫條件已被其他操作修改，請重新開啟。')
            if self.editing and self.name.text().strip() != self.editing and self.name.text().strip() in self.db.new_api.pref('virtual_libraries', {}):
                raise ValueError('新名稱已被其他虛擬書庫使用，請換一個名稱。')
            if getattr(self, 'raw_mode', False):
                search = self.raw.toPlainText().strip()
                if not search:
                    raise ValueError('搜尋條件不可空白。')
                return [(self.name.text(), search)], 'update' if self.editing else 'skip'
            entries = [(self.name.text(), self.conditions.generated())]
        else:
            field = self.batch_field.currentData()
            template = self.template.text()
            if '{值}' not in template:
                raise ValueError('批次名稱範本須包含 {值}。')
            entries = []
            for row in range(self.values.rowCount()):
                item = self.values.item(row, 0)
                if item.checkState() == Qt.CheckState.Checked:
                    term = item.text()
                    name = template.replace('{欄位}', self.metadata[field].get('name') or field).replace('{值}', term)
                    entries.append((name, core.condition(field, self.metadata[field]['datatype'], 'eq', term)))
        return entries, 'update' if self.tabs.currentIndex() == 0 and self.editing else ('skip', 'rename', 'update')[self.conflict.currentIndex()] if self.tabs.currentIndex() == 1 else 'skip'

    def preview(self):
        try:
            self.preview_input = self.inputs()
            self.expected = dict(self.db.new_api.pref('virtual_libraries', {}))
            self.rows = core.plan(self.db, *self.preview_input)
            self.results.setRowCount(len(self.rows))
            ids = set()
            for row, (name, search, count, status) in enumerate(self.rows):
                for col, text in enumerate((name, str(count), status, search)):
                    self.results.setItem(row, col, QTableWidgetItem(text))
                ids.update(self.db.new_api.search(search))
            sample = sorted(ids)[:50]
            self.books.setPlainText('\n'.join(str(self.db.new_api.field_for('title', bid)) + ' — ' + '、'.join(self.db.new_api.field_for('authors', bid)) for bid in sample))
            active = sum(row[3] != '跳過' for row in self.rows)
            if self.tabs.currentIndex() == 0:
                self.summary.setText(f'符合 {len(ids)} 本（整個實體書庫）' + ('；同名已存在，請從左側選取修改。' if not active else ''))
            else:
                self.summary.setText(f'將建立／更新 {active} 個書庫，符合書籍共 {len(ids)} 本（去重）。')
            return True
        except Exception as err:
            error_dialog(self, '無法預覽', str(err), show=True)
            return False

    def create_libraries(self):
        try:
            if not self.preview():
                return
            fresh = core.plan(self.db, *self.preview_input)
            if fresh != self.rows:
                raise ValueError('預覽本數或名稱已變更，請重新預覽。')
            active = [row for row in self.rows if row[3] != '跳過']
            if not active:
                return
            # The Save button is the confirmation for a single-library edit.
            if self.tabs.currentIndex() == 1:
                message = f'將批次建立／更新 {len(active)} 個虛擬書庫，其中更新 {sum(row[3] == "更新" for row in active)} 個。是否繼續？'
                if not question_dialog(self, '確認批次儲存', message, default_yes=False):
                    return
            if self.inputs() != self.preview_input:
                raise ValueError('確認期間條件已變更，請重試。')
            renamed = self.editing if self.tabs.currentIndex() == 0 and self.editing and active[0][0] != self.editing else None
            core.save(self.db, self.rows, self.expected, rename_from=renamed)
            self.gui.library_view.model().refresh()
            if renamed:
                self.gui.virtual_libraries_changed(renamed=((renamed, active[0][0]),))
            else:
                self.gui.virtual_libraries_changed()
            if self.activate.isChecked() and active:
                self.gui.apply_virtual_library(active[0][0])
            self.accept()
        except Exception as err:
            error_dialog(self, '無法建立', str(err), show=True)
