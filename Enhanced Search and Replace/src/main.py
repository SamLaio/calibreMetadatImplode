from qt.core import (QAction, QDialog, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, Qt, QMessageBox, QTextCursor, QLabel,
    QFormLayout, QHeaderView, QComboBox, QToolButton, QMenu)
from calibre.gui2.tweak_book.plugin import Tool
from calibre.gui2.tweak_book import editors
from calibre.gui2.tweak_book.editor import syntax_from_mime
from pathlib import PurePosixPath
from calibre_plugins.text_regex_p0.core import search, replace, utf16, update_preview

class ReplacementPreviewError(ValueError):
    pass

def text_syntax(name, mime):
    mime = mime or ''
    syntax = syntax_from_mime(name, mime)
    suffix = PurePosixPath(name).suffix.lower()
    if mime in {'application/json', 'application/ld+json'} or mime.endswith('+json') or suffix == '.json':
        return 'json'
    if syntax in {'html', 'xml', 'css', 'javascript', 'text'}:
        return syntax
    if mime.startswith('text/'):
        return 'text'
    return None

class SearchDialog(QDialog):
    def __init__(self, tool):
        super().__init__(tool.gui)
        self.tool = tool
        self.setWindowTitle('Enhanced Search and Replace')
        self.resize(800, 420)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel('搜尋勾選的文字類型：HTML 內文／其他檔案原始碼。支援 $1 與 \\g<1>。'))
        self.pattern = QLineEdit()
        self.template = QLineEdit()
        fields = QFormLayout()
        fields.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        search_fields = QHBoxLayout()
        search_fields.addWidget(self.pattern, 1)
        self.types = QToolButton()
        self.types.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.types_menu = QMenu(self.types)
        self.types.setMenu(self.types_menu)
        self.type_actions = {}
        self.file_types = {}
        self.types_menu.aboutToShow.connect(self.refresh_types)
        search_fields.addWidget(self.types)
        fields.addRow('尋找：', search_fields)
        replacement_fields = QHBoxLayout()
        replacement_fields.addWidget(self.template, 1)
        self.mode = QComboBox()
        self.mode.addItem('純文字（保留 HTML）', 'text')
        self.mode.addItem('HTML 片段', 'html')
        self.mode.setToolTip('HTML 內文：保留標籤或插入完整片段；其他文字類型一律取代原始碼')
        replacement_fields.addWidget(self.mode)
        fields.addRow('取代為：', replacement_fields)
        layout.addLayout(fields)
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(['勾選', '原文', '取代預覽', '來源位置', '狀態／原因', '檔案'])
        header = self.table.horizontalHeader()
        header.setSectionsClickable(True)
        header.sectionClicked.connect(self.toggle_checks)
        self.table.horizontalHeaderItem(0).setToolTip('點擊全選／全部取消勾選')
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        for column, width in enumerate((54, 140, 140, 90, 120, 200)):
            header.resizeSection(column, width)
        layout.addWidget(self.table, 1)
        buttons = QHBoxLayout()
        layout.addLayout(buttons)
        for title, callback in [('搜尋', self.scan), ('定位', self.locate), ('逐筆取代', self.single), ('取代勾選', self.batch)]:
            button = QPushButton(title)
            button.clicked.connect(lambda checked=False, cb=callback: self.guard(cb))
            buttons.addWidget(button)
        self.table.cellDoubleClicked.connect(lambda *args: self.guard(self.locate))
        self.table.cellClicked.connect(self.position_clicked)
        self.rows = []
        self.preview_warning_shown = False
        self.pattern.textChanged.connect(self.invalidate)
        self.template.textChanged.connect(self.refresh_previews)
        self.mode.currentIndexChanged.connect(self.refresh_previews)
        self.refresh_types()

    def refresh_types(self):
        container = self.tool.current_container
        self.file_types = {}
        if container is not None:
            for name, mime in container.mime_map.items():
                syntax = text_syntax(name, mime)
                if syntax:
                    label = PurePosixPath(name).suffix.lstrip('.').upper() or syntax.upper()
                    self.file_types[name] = (label, syntax)
        labels = sorted({label for label, syntax in self.file_types.values()})
        if labels != sorted(self.type_actions):
            checked = {label: action.isChecked() for label, action in self.type_actions.items()}
            self.types_menu.clear()
            self.type_actions = {}
            self.types_menu.addAction('全選文字類型', lambda: self.set_types(True))
            self.types_menu.addAction('全部取消', lambda: self.set_types(False))
            self.types_menu.addSeparator()
            for label in labels:
                action = self.types_menu.addAction(label)
                action.setCheckable(True)
                action.setChecked(checked.get(label, True))
                action.toggled.connect(self.types_changed)
                self.type_actions[label] = action
            self.types_changed()
        else:
            self.update_types_label()

    def set_types(self, checked):
        for action in self.type_actions.values():
            action.setChecked(checked)

    def update_types_label(self):
        selected = [label for label, action in self.type_actions.items() if action.isChecked()]
        self.types.setText('類型：全部文字' if selected and len(selected) == len(self.type_actions)
                           else f'類型：已選 {len(selected)}/{len(self.type_actions)}')
        self.types.setToolTip('搜尋類型：' + ('、'.join(selected) if selected else '未選取'))

    def types_changed(self):
        self.update_types_label()
        self.invalidate()

    def toggle_checks(self, column):
        if column != 0 or not self.rows:
            return
        items = [self.table.item(i, 0) for i, row in enumerate(self.rows) if not row.get('done')]
        state = (Qt.CheckState.Unchecked if all(item.checkState() == Qt.CheckState.Checked for item in items)
                 else Qt.CheckState.Checked)
        for item in items:
            item.setCheckState(state)

    def refresh_previews(self):
        for i, row in enumerate(self.rows):
            if 'match' not in row or row.get('done'):
                continue
            update_preview(row, self.template.text(), self.mode.currentData())
            for column, value in ((2, row['after']), (4, row['reason'])):
                self.table.item(i, column).setText(value)
                self.table.item(i, column).setToolTip(value)

    def invalidate(self):
        self.rows = []
        self.table.setRowCount(0)

    def guard(self, callback):
        try:
            callback()
        except Exception as err:
            if isinstance(err, ReplacementPreviewError):
                if self.preview_warning_shown:
                    return
                self.preview_warning_shown = True
            QMessageBox.warning(self, 'Enhanced Search and Replace', str(err))

    def scan(self):
        self.invalidate()
        self.preview_warning_shown = False
        self.container = self.tool.current_container
        if self.container is None:
            raise ValueError('請先開啟要搜尋的書籍')
        if not self.pattern.text():
            raise ValueError('請輸入尋找內容')
        self.refresh_types()
        selected_types = {label for label, action in self.type_actions.items() if action.isChecked()}
        if not selected_types:
            raise ValueError('請至少勾選一種文字檔案類型')
        self.snapshots = {}
        names = dict.fromkeys([name for name, linear in self.container.spine_names] + sorted(self.container.mime_map))
        errors = []
        for name in names:
            if name not in self.file_types or self.file_types[name][0] not in selected_types:
                continue
            try:
                raw = self.read_source(name)
                found = search(raw, self.pattern.text(), self.template.text(), self.mode.currentData(), self.file_types[name][1])
                self.snapshots[name] = raw
                self.rows.extend(dict(row, name=name) for row in found)
            except Exception as err:
                message = f'{name}：{err}'
                errors.append(message)
                self.rows.append(dict(name=name, before='', after='', start=0, end=0,
                                      safe=False, error=message, reason=message))
        self.table.setRowCount(len(self.rows))
        for i, row in enumerate(self.rows):
            check = QTableWidgetItem()
            check.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            check.setCheckState(Qt.CheckState.Unchecked)
            self.table.setItem(i, 0, check)
            for j, value in enumerate([row['before'], row['after'], str(row['start']), row['reason'], row['name']], 1):
                item = QTableWidgetItem(value)
                item.setToolTip(value)
                item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                self.table.setItem(i, j, item)
        if errors:
            raise ValueError('\n'.join(dict.fromkeys(errors)) + '\n其他搜尋結果已保留；請修正錯誤後重新搜尋。')

    def read_source(self, name):
        if name in editors:
            return str(editors[name].editor.toPlainText())
        data = self.tool.current_container.raw_data(name, normalize_to_nfc=False)
        return data.decode('utf-8') if isinstance(data, bytes) else data

    def fresh(self, names=None):
        if not self.rows:
            raise ValueError('請先搜尋；修改尋找式後須重新搜尋')
        if self.tool.current_container is not self.container:
            raise ValueError('書籍或內容已變更，請重新搜尋')
        for name in names if names is not None else self.snapshots:
            if name not in self.snapshots or self.read_source(name) != self.snapshots[name]:
                raise ValueError(f'{name}：內容已變更，請重新搜尋')

    def open_editor(self, name):
        syntax = self.file_types[name][1]
        ed = self.tool.boss.edit_file(name, syntax='text' if syntax == 'json' else syntax)
        if ed is None or str(ed.editor.toPlainText()) != self.snapshots[name]:
            raise ValueError(f'{name}：開啟後內容已變更，請重新搜尋')
        return ed

    def position_clicked(self, row, column):
        if column == 3:
            self.table.setCurrentCell(row, column)
            self.guard(self.locate)

    def locate(self):
        i = self.table.currentRow()
        if i < 0:
            raise ValueError('請選取一列')
        row = self.rows[i]
        self.fresh([row['name']])
        if row['start'] == row['end'] and not row.get('done'):
            raise ValueError('此結果沒有可定位的來源範圍')
        text = self.open_editor(row['name']).editor
        cursor = text.textCursor()
        cursor.setPosition(utf16(self.snapshots[row['name']], row['start']))
        cursor.setPosition(utf16(self.snapshots[row['name']], row['end']), QTextCursor.MoveMode.KeepAnchor)
        text.setTextCursor(cursor)
        text.ensureCursorVisible()

    def single(self):
        i = self.table.currentRow()
        if i < 0:
            raise ValueError('請選取一列')
        row = self.rows[i]
        self.apply([row])
        for j in range(i + 1, len(self.rows)):
            if not self.rows[j].get('done'):
                self.table.setCurrentCell(j, 1)
                self.table.scrollToItem(self.table.item(j, 1))
                break
        else:
            self.table.clearSelection()
            self.table.setCurrentItem(None)

    def batch(self):
        self.apply([row for i, row in enumerate(self.rows)
                    if not row.get('done') and self.table.item(i,0).checkState() == Qt.CheckState.Checked])

    def apply(self, rows):
        if not rows:
            raise ValueError('尚未勾選結果')
        if any(row.get('done') for row in rows):
            raise ValueError('此結果已取代，請選取尚未處理的結果')
        stage = '驗證結果'
        checkpoint = False
        rolled_back = False
        preview_failure = False
        try:
            names = list(dict.fromkeys(row['name'] for row in rows))
            self.fresh(names)
            preview_failure = any(row.get('error') for row in rows)
            changes = {name: replace(self.snapshots[name], [row for row in rows if row['name'] == name]) for name in names}
            if len(names) == 1:
                ed = self.open_editor(names[0])
                stage = '寫入編輯器'
                ed.replace_data(changes[names[0]])
                stage = '同步書籍內容'
                self.tool.boss.commit_all_editors_to_container()
            else:
                stage = '建立整批復原點'
                self.tool.boss.add_savepoint('增強搜尋與取代：取代勾選')
                checkpoint = True
                stage = '寫入書籍內容'
                for name, raw in changes.items():
                    with self.tool.current_container.open(name, 'wb') as stream:
                        stream.write(raw.encode('utf-8'))
                if self.tool.current_container.opf_name in changes:
                    self.tool.current_container.refresh_mime_map()
                stage = '同步編輯視窗'
                self.tool.boss.apply_container_update_to_gui()
        except Exception as err:
            if checkpoint:
                try:
                    self.tool.boss.rewind_savepoint()
                    self.tool.boss.apply_container_update_to_gui()
                    rolled_back = True
                except Exception as rollback_error:
                    err = RuntimeError(f'{err}；回復失敗：{rollback_error}')
            details = []
            selected_ids = {id(row) for row in rows}
            for i, row in enumerate(self.rows):
                if id(row) in selected_ids:
                    reason = str(err)
                    if stage == '驗證結果' and not row['safe']:
                        reason += '；' + row['reason']
                    message = f'取代失敗（{stage}）：{reason}'
                    self.table.item(i, 4).setText(message)
                    self.table.item(i, 4).setToolTip(message)
                    details.append(f"{row['name']} 第 {i + 1} 筆「{row['before']}」（來源位置 {row['start']}）：{reason}")
            state = '尚未寫入內容。' if stage == '驗證結果' else '編輯器可能已變更，請先檢查內容；需要時使用復原。'
            if rolled_back:
                state = '本次跨檔變更已整批回復。'
            error_type = ReplacementPreviewError if stage == '驗證結果' and preview_failure else ValueError
            raise error_type(f"取代失敗：{stage}\n{state}\n" + '\n'.join(details)) from err
        self.container = self.tool.current_container
        self.snapshots.update(changes)
        selected_ids = {id(row) for row in rows}
        edits = {name: [(row['start'], row['end'], len(row['replacement']))
                        for row in rows if row['name'] == name] for name in names}
        for i, row in enumerate(self.rows):
            shift = sum(length - (end - start) for start, end, length in edits.get(row['name'], [])
                        if end <= row['start'])
            row['start'] += shift
            row['end'] += shift
            if id(row) in selected_ids:
                row.update(done=True, safe=False, error='', reason='已取代')
                row['end'] = row['start'] + len(row['replacement'])
                check = self.table.item(i, 0)
                check.setCheckState(Qt.CheckState.Unchecked)
                check.setFlags(Qt.ItemFlag.NoItemFlags)
                self.table.item(i, 4).setText('已取代')
                self.table.item(i, 4).setToolTip('已取代；重新搜尋可取得目前內容')
            self.table.item(i, 3).setText(str(row['start']))

class TextRegexP0(Tool):
    name = 'text-regex-p0'
    def create_action(self, for_toolbar=True):
        action = QAction(get_icons('images/search-replace.svg'), 'Enhanced Search and Replace', self.gui)
        action.setToolTip('搜尋全書勾選的文字檔案類型，預覽並取代結果')
        action.triggered.connect(self.open_dialog)
        return action

    def open_dialog(self):
        self.dialog = SearchDialog(self)
        self.dialog.show()
