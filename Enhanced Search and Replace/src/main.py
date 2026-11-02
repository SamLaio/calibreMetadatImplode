from qt.core import (QAction, QDialog, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QTableView, Qt, QMessageBox, QTextCursor, QLabel,
    QFormLayout, QHeaderView, QComboBox, QToolButton, QMenu, QProgressBar, QTimer, QModelIndex, QApplication, QAbstractButton)
from calibre.gui2.tweak_book.plugin import Tool
from calibre.gui2.tweak_book import editors
from calibre.gui2.tweak_book.editor import syntax_from_mime
from pathlib import PurePosixPath
from bisect import bisect_right
from calibre_plugins.text_regex_p0.core import replace, utf16, update_preview
from calibre_plugins.text_regex_p0.results import ResultsModel, ResultsFilter
from calibre_plugins.text_regex_p0.search_worker import SearchWorker

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
        description = QLabel('HTML 可選內文／原始碼；其他文字檔搜尋原始碼。支援 $1 與 \\g<1>。')
        description.setWordWrap(True)
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
        self.search_mode = QComboBox()
        self.search_mode.addItem('HTML：內文', 'html')
        self.search_mode.addItem('HTML：原始碼', 'xml')
        self.search_mode.setToolTip('只影響 HTML／XHTML；其他文字檔一律搜尋原始碼')
        search_fields.addWidget(self.search_mode)
        types_row = QHBoxLayout()
        types_row.addWidget(description, 1)
        types_row.addWidget(self.types)
        layout.addLayout(types_row)
        fields.addRow('尋找：', search_fields)
        replacement_fields = QHBoxLayout()
        replacement_fields.addWidget(self.template, 1)
        self.mode = QComboBox()
        self.mode.addItem('純文字（保留 HTML）', 'text')
        self.mode.addItem('HTML 片段', 'html')
        self.mode.setToolTip('HTML 內文：保留標籤或插入完整片段；原始碼搜尋一律以原始碼取代')
        replacement_fields.addWidget(self.mode)
        fields.addRow('取代為：', replacement_fields)
        layout.addLayout(fields)
        self.filter = QComboBox()
        for label, value in [('全部結果', 'all'), ('待處理', 'pending'), ('已取代', 'done'), ('失敗／需確認', 'failed')]:
            self.filter.addItem(label, value)
        layout.addWidget(self.filter)
        self.model = ResultsModel(self)
        self.proxy = ResultsFilter(self)
        self.proxy.setSourceModel(self.model)
        self.table = QTableView()
        self.table.setModel(self.proxy)
        self.corner_button = self.table.findChild(QAbstractButton)
        self.corner_button.clicked.disconnect()
        self.corner_button.clicked.connect(lambda: self.toggle_checks(0))
        self.corner_button.setToolTip('全選／取消目前可見且尚未完成的結果')
        self.corner_button.setAccessibleName('全選／取消全選')
        corner_layout = QHBoxLayout(self.corner_button)
        corner_layout.setContentsMargins(0, 0, 0, 0)
        corner_label = QLabel('全選')
        corner_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        corner_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        corner_layout.addWidget(corner_label)
        self.table.verticalHeader().setMinimumWidth(self.table.fontMetrics().horizontalAdvance('全選') + 16)
        self.table.setWordWrap(False)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.table.verticalHeader().setDefaultSectionSize(self.table.fontMetrics().height() + 12)
        header = self.table.horizontalHeader()
        header.setSectionsClickable(True)
        header.sectionClicked.connect(self.header_clicked)
        header.setSortIndicatorShown(True)
        header.setSortIndicator(-1, Qt.SortOrder.AscendingOrder)
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        for column, width in enumerate((54, 140, 140, 90, 120, 200)):
            header.resizeSection(column, width)
        layout.addWidget(self.table, 1)
        self.progress = QProgressBar()
        self.progress.setRange(0, 1000)
        self.status = QLabel('尚未搜尋')
        self.cancel_button = QPushButton('取消搜尋')
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self.cancel_search)
        progress_layout = QHBoxLayout()
        progress_layout.addWidget(self.progress, 1)
        progress_layout.addWidget(self.cancel_button)
        layout.addLayout(progress_layout)
        layout.addWidget(self.status)
        buttons = QHBoxLayout()
        layout.addLayout(buttons)
        self.action_buttons = []
        for title, callback in [('搜尋', self.scan), ('定位', self.locate), ('逐筆取代', self.single), ('取代勾選', self.batch)]:
            button = QPushButton(title)
            button.clicked.connect(lambda checked=False, cb=callback: self.guard(cb))
            buttons.addWidget(button)
            self.action_buttons.append(button)
        self.table.doubleClicked.connect(lambda index: self.guard(self.locate))
        self.table.clicked.connect(self.position_clicked)
        self.rows = []
        self.worker = None
        self.busy = False
        self.closing = False
        self.preview_warning_shown = False
        self.pattern.textChanged.connect(self.invalidate)
        self.template.textChanged.connect(self.refresh_previews)
        self.mode.currentIndexChanged.connect(self.refresh_previews)
        self.search_mode.currentIndexChanged.connect(self.invalidate)
        self.filter.currentIndexChanged.connect(self.filter_changed)
        self.refresh_types()
        QApplication.instance().aboutToQuit.connect(self.shutdown_search)
        self.ensurePolished()
        table_height = (15 * self.table.verticalHeader().defaultSectionSize()
                        + self.table.horizontalHeader().sizeHint().height()
                        + self.table.horizontalScrollBar().sizeHint().height()
                        + 2 * self.table.frameWidth())
        height = layout.sizeHint().height() - self.table.sizeHint().height() + table_height
        self.resize(self.width(), min(height, self.screen().availableGeometry().height() - 64))

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

    def current_row(self):
        index = self.proxy.mapToSource(self.table.currentIndex())
        return index.row() if index.isValid() else -1

    def select_row(self, row, column=1):
        index = self.proxy.mapFromSource(self.model.index(row, column))
        self.table.setCurrentIndex(index)
        if index.isValid():
            self.table.scrollTo(index)

    def visible_rows(self):
        return [self.proxy.mapToSource(self.proxy.index(i, 0)).row() for i in range(self.proxy.rowCount())]

    def header_clicked(self, column):
        if column == 0:
            self.table.horizontalHeader().setSortIndicator(self.proxy.sortColumn(), self.proxy.sortOrder())
        else:
            header = self.table.horizontalHeader()
            order = Qt.SortOrder.DescendingOrder if header.sortIndicatorSection() == column and header.sortIndicatorOrder() == Qt.SortOrder.AscendingOrder else Qt.SortOrder.AscendingOrder
            header.setSortIndicator(column, order)
            self.proxy.sort(column, order)

    def filter_changed(self):
        self.proxy.status = self.filter.currentData()
        self.proxy.invalidate()

    def results_changed(self):
        self.model.changed()
        self.proxy.invalidate()

    def toggle_checks(self, column):
        if column != 0 or self.busy:
            return
        rows = [self.rows[i] for i in self.visible_rows() if not self.rows[i].get('done')]
        checked = not all(row.get('checked') for row in rows)
        for row in rows:
            row['checked'] = checked
        self.model.changed()

    def refresh_previews(self):
        if self.busy:
            return
        self.preview_generation = getattr(self, 'preview_generation', 0) + 1
        generation = self.preview_generation
        template, mode = self.template.text(), self.mode.currentData()
        self.preview_pending = True
        def update_chunk(start=0):
            if generation != self.preview_generation:
                return
            for row in self.rows[start:start + 200]:
                if 'match' in row and not row.get('done'):
                    update_preview(row, template, mode)
                    row.pop('failed', None)
            if start + 200 < len(self.rows):
                QTimer.singleShot(0, lambda: update_chunk(start + 200))
            else:
                self.preview_pending = False
                self.results_changed()
        update_chunk()

    def invalidate(self):
        self.preview_generation = getattr(self, 'preview_generation', 0) + 1
        self.preview_pending = False
        self.rows = []
        self.model.reset_rows(self.rows)

    def guard(self, callback):
        try:
            callback()
        except Exception as err:
            if isinstance(err, ReplacementPreviewError):
                if self.preview_warning_shown:
                    return
                self.preview_warning_shown = True
            QMessageBox.warning(self, 'Enhanced Search and Replace', str(err))

    def set_busy(self, busy):
        self.busy = busy
        for widget in [self.pattern, self.template, self.types, self.mode, self.search_mode, *self.action_buttons]:
            widget.setEnabled(not busy)
        self.cancel_button.setEnabled(busy)

    def scan(self):
        if self.busy:
            return
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
        names = dict.fromkeys([name for name, linear in self.container.spine_names] + sorted(self.container.mime_map))
        self.search_names = [name for name in names if name in self.file_types and self.file_types[name][0] in selected_types]
        self.tasks = []
        self.capture_position = 0
        self.search_cancelled = False
        self.progress.setValue(0)
        self.status.setText('準備搜尋內容…')
        self.set_busy(True)
        QTimer.singleShot(0, self.capture_next)

    def capture_next(self):
        if not self.busy or self.worker is not None:
            return
        if self.search_cancelled or self.tool.current_container is not self.container:
            self.status.setText('搜尋已取消')
            self.set_busy(False)
            return
        if self.capture_position < len(self.search_names):
            name = self.search_names[self.capture_position]
            syntax = self.file_types[name][1]
            if syntax == 'html' and self.search_mode.currentData() == 'xml':
                syntax = 'xml'
            raw = str(editors[name].editor.toPlainText()) if name in editors else None
            self.tasks.append((name, syntax, raw))
            self.capture_position += 1
            self.status.setText(f'準備 {self.capture_position}/{len(self.search_names)}：{name}')
            QTimer.singleShot(0, self.capture_next)
            return
        self.worker = SearchWorker(self.container, self.tasks, self.pattern.text(), self.template.text(), self.mode.currentData(), self)
        self.worker.progress.connect(self.search_progress)
        self.worker.completed.connect(self.search_completed)
        self.worker.finished.connect(self.search_finished)
        self.worker.start()

    def search_progress(self, value, message):
        self.progress.setValue(value)
        self.status.setText(message)

    def search_completed(self, result):
        rows, snapshots, errors, cancelled, fatal = result
        if self.closing:
            return
        if self.tool.current_container is not self.container:
            self.status.setText('書籍已切換，搜尋結果已丟棄')
            return
        self.rows, self.snapshots = rows, snapshots
        self.model.reset_rows(rows)
        self.status.setText(f'{"已取消，保留已完成檔案" if cancelled else "搜尋完成"}：{len(rows)} 筆結果')
        if not cancelled:
            self.progress.setValue(1000)
        if fatal or errors:
            QMessageBox.warning(self, 'Enhanced Search and Replace', fatal or '\n'.join(dict.fromkeys(errors)))

    def search_finished(self):
        worker, self.worker = self.worker, None
        worker.deleteLater()
        self.set_busy(False)
        if self.closing:
            self.close()

    def cancel_search(self):
        self.search_cancelled = True
        if self.worker is not None:
            self.worker.requestInterruption()
        self.status.setText('正在取消搜尋…')

    def shutdown_search(self):
        if self.worker is not None:
            self.worker.requestInterruption()
            self.worker.wait()

    def closeEvent(self, event):
        if self.busy:
            self.closing = True
            self.cancel_search()
            if self.worker is not None:
                event.ignore()
                return
            self.set_busy(False)
        event.accept()

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

    def position_clicked(self, index):
        if index.column() == 3:
            self.table.setCurrentIndex(index)
            self.guard(self.locate)

    def locate(self):
        i = self.current_row()
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
        i = self.current_row()
        if i < 0:
            raise ValueError('請選取一列')
        row = self.rows[i]
        visible = self.visible_rows()
        following = visible[visible.index(i) + 1:]
        self.apply([row])
        for j in following:
            if not self.rows[j].get('done') and self.proxy.mapFromSource(self.model.index(j, 0)).isValid():
                self.select_row(j)
                break
        else:
            self.table.clearSelection()
            self.table.setCurrentIndex(QModelIndex())

    def batch(self):
        self.apply([self.rows[i] for i in self.visible_rows()
                    if not self.rows[i].get('done') and self.rows[i].get('checked')])

    def apply(self, rows):
        if self.busy or getattr(self, 'preview_pending', False):
            raise ValueError('搜尋或預覽更新中，請稍候')
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
                    row.update(failed=True, reason=message)
                    details.append(f"{row['name']} 第 {i + 1} 筆「{row['before']}」（來源位置 {row['start']}）：{reason}")
            self.results_changed()
            state = '尚未寫入內容。' if stage == '驗證結果' else '編輯器可能已變更，請先檢查內容；需要時使用復原。'
            if rolled_back:
                state = '本次跨檔變更已整批回復。'
            error_type = ReplacementPreviewError if stage == '驗證結果' and preview_failure else ValueError
            raise error_type(f"取代失敗：{stage}\n{state}\n" + '\n'.join(details)) from err
        self.container = self.tool.current_container
        self.snapshots.update(changes)
        selected_ids = {id(row) for row in rows}
        edits = {}
        for name in names:
            delta, ends, shifts = 0, [], [0]
            for row in sorted((row for row in rows if row['name'] == name), key=lambda row: row['end']):
                delta += len(row['replacement']) - (row['end'] - row['start'])
                ends.append(row['end'])
                shifts.append(delta)
            edits[name] = (ends, shifts)
        for row in self.rows:
            ends, shifts = edits.get(row['name'], ([], [0]))
            shift = shifts[bisect_right(ends, row['start'])]
            row['start'] += shift
            row['end'] += shift
            if id(row) in selected_ids:
                row.update(done=True, checked=False, failed=False, safe=False, error='', reason='已取代')
                row['end'] = row['start'] + len(row['replacement'])
        self.results_changed()


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
