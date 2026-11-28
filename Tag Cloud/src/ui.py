from qt.core import (
    QComboBox, QHBoxLayout, QIcon, QLabel, QLineEdit, QPushButton,
    QSplitter, QTextBrowser, QTimer, QToolButton, QVBoxLayout, QWidget, Qt,
    QDialog, QDialogButtonBox, QCheckBox, QColor, QColorDialog,
    QListWidget, QListWidgetItem,
    QAction,
)
from calibre.gui2 import error_dialog, gprefs, config
from calibre.gui2.actions import InterfaceAction
from calibre.gui2.widgets import HistoryLineEdit
from calibre.utils.config import JSONConfig
from calibre.utils.icu import sort_key
from calibre_plugins.tag_cloud.core import indexed_terms, font_size, tag_query, book_query
from html import escape
import hashlib
import random

prefs = JSONConfig('plugins/tag_cloud')
prefs.defaults.update(visible=True, sizes=[600, 300], limit=100, match_all=True, scope=0, field='tags')
prefs.defaults.update(random_colors=True, colors=['#56b4e9', '#e69f00', '#009e73', '#cc79a7', '#d55e00'])
prefs.defaults['click_mode'] = 'intersection'
prefs.defaults['order'] = 'random'
prefs.defaults['enabled_fields'] = {}
prefs.defaults.update(display_mode='sidebar', floating_geometry='')


class CloudPanel(QWidget):
    def __init__(self, action):
        super().__init__(action.gui)
        self.action = action
        self.selected = []
        self.counts = []
        self.names = []
        self.base_query = None
        self.last_query = None
        self.order_seed = random.random()
        self.category_order = {}
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)
        header = QHBoxLayout()
        refresh = QToolButton(self)
        refresh.setIcon(QIcon.ic('view-refresh.png'))
        refresh.setAccessibleName('重新統計標籤')
        refresh.setToolTip('重新統計標籤')
        refresh.clicked.connect(self.reload)
        header.addWidget(refresh)
        settings = QToolButton(self)
        settings.setIcon(QIcon.ic('gear.png'))
        settings.setAccessibleName('標籤雲設定')
        settings.setToolTip('設定欄位與字體顏色')
        settings.clicked.connect(self.configure)
        header.addWidget(settings)
        self.field = QComboBox(self)
        self.field.setAccessibleName('統計欄位')
        self.field.hide()
        self.populate_fields()
        self.scope = QComboBox(self)
        self.scope.addItems(['目前虛擬書庫', '整個書庫'])
        self.scope.setCurrentIndex(prefs['scope'])
        self.scope.setAccessibleName('統計範圍')
        self.limit = QComboBox(self)
        self.limit.addItems(['50', '100', '200', '500', '全部'])
        saved_limit = str(prefs['limit'])
        self.limit.setCurrentText(saved_limit if saved_limit in ('50', '100', '200', '500', '全部') else '100')
        self.limit.setAccessibleName('顯示標籤數量')
        self.scope.hide()
        self.limit.hide()
        self.find = HistoryLineEdit(self)
        self.find.initialize('tag_cloud_search')
        self.find.setMinimumContentsLength(5)
        self.find.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.find.lineEdit().setPlaceholderText('搜尋標籤……')
        self.clear_search = self.find.lineEdit().addAction(QIcon.ic('window-close.png'), QLineEdit.ActionPosition.LeadingPosition)
        self.clear_search.setToolTip('清除搜尋')
        self.clear_search.triggered.connect(lambda: self.find.setText(''))
        self.find.setAccessibleName('搜尋標籤')
        header.insertWidget(0, self.find, 1)
        self.search_button = QToolButton(self)
        self.search_button.setAutoRaise(True)
        self.search_button.setIcon(QIcon.ic('search.png'))
        self.search_button.setToolTip('搜尋標籤（Enter）')
        self.search_button.setAccessibleName('搜尋標籤')
        self.search_button.clicked.connect(self.search_words)
        header.insertWidget(1, self.search_button)
        self.find.lineEdit().returnPressed.connect(self.search_words)
        self.find.textActivated.connect(self.search_words)
        self.cloud = QTextBrowser(self)
        self.cloud.setOpenLinks(False)
        self.cloud.setAccessibleName('標籤雲；點選標籤篩選書籍')
        self.cloud.anchorClicked.connect(self.clicked)
        self.cloud.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.cloud.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.cloud)
        layout.addLayout(header)
        self.status = QLabel(self)
        self.status.setWordWrap(True)
        self.status.hide()
        self.mode = QComboBox(self)
        self.mode.addItems(['交集', '獨選'])
        self.mode.setCurrentIndex(1 if prefs['click_mode'] == 'single' else 0)
        self.mode.hide()
        self.order = QComboBox(self)
        self.order.addItems(['跟隨標籤瀏覽器', '隨機排列'])
        self.order.setCurrentIndex(0 if prefs['order'] == 'browser' else 1)
        self.order.hide()
        self.scope.currentIndexChanged.connect(self.reload)
        self.field.currentIndexChanged.connect(self.change_field)
        self.limit.currentIndexChanged.connect(self.render)
        self.find.editTextChanged.connect(self.render)
        self.mode.currentIndexChanged.connect(self.change_click_mode)
        self.order.currentIndexChanged.connect(self.change_order)

    def available_fields(self):
        metadata = self.action.gui.current_db.new_api.field_metadata
        fields = []
        keys = ['authors', 'tags', 'publisher'] + [key for key in metadata if key not in ('authors', 'tags', 'publisher')]
        for key in keys:
            info = metadata[key]
            if info['datatype'] is not None:
                fields.append((key, (info['name'] or key) + ' (' + key + ')'))
        return fields

    def show_context_menu(self, position):
        from calibre_plugins.tag_cloud.context import show_menu
        show_menu(self, position)

    def enabled_fields(self):
        library = self.action.gui.current_db.new_api.library_id
        return prefs['enabled_fields'].get(library, ['authors', 'tags', 'publisher'])

    def save_enabled_fields(self, fields):
        libraries = dict(prefs['enabled_fields'])
        libraries[self.action.gui.current_db.new_api.library_id] = list(fields)
        prefs['enabled_fields'] = libraries

    def populate_fields(self, enabled=None, selector=None):
        selector = self.field if selector is None else selector
        selected = selector.currentData() or prefs['field']
        enabled = self.enabled_fields() if enabled is None else enabled
        selector.blockSignals(True)
        selector.clear()
        for key, label in self.available_fields():
            if key in enabled:
                selector.addItem(label, key)
        selector.setCurrentIndex(max(0, selector.findData(selected)))
        selector.blockSignals(False)

    def choose_fields(self, enabled, parent):
        dialog = QDialog(parent)
        dialog.setWindowTitle('選擇詞雲欄位')
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel('只有勾選的欄位會出現在下拉選單；依目前書庫保存。'))
        listing = QListWidget(dialog)
        for key, label in self.available_fields():
            item = QListWidgetItem(label, listing)
            item.setData(Qt.ItemDataRole.UserRole, key)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked if key in enabled else Qt.CheckState.Unchecked)
        layout.addWidget(listing)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        dialog.resize(480, 500)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return [listing.item(i).data(Qt.ItemDataRole.UserRole) for i in range(listing.count())
                    if listing.item(i).checkState() == Qt.CheckState.Checked]

    def search_words(self, *args):
        self.find.save_history()
        self.render()

    def change_order(self, *args):
        prefs['order'] = 'browser' if self.order.currentIndex() == 0 else 'random'
        self.render()

    def change_field(self, *args):
        self.clear()
        prefs['field'] = self.field.currentData()
        self.reload()

    def configure(self):
        dialog = QDialog(self)
        dialog.setWindowTitle('Tag Cloud 0.1.7 — 設定')
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel('雲的統計與篩選欄位'))
        field_row = QHBoxLayout()
        field = QComboBox(dialog)
        for index in range(self.field.count()):
            field.addItem(self.field.itemText(index), self.field.itemData(index))
        field.setCurrentIndex(self.field.currentIndex())
        field_row.addWidget(field, 1)
        fields_button = QToolButton(dialog)
        fields_button.setIcon(QIcon.ic('gear.png'))
        fields_button.setToolTip('勾選下拉選單可用的欄位')
        fields_button.setAccessibleName('選擇詞雲欄位')
        field_row.addWidget(fields_button)
        layout.addLayout(field_row)
        enabled = list(self.enabled_fields())
        def edit_fields():
            result = self.choose_fields(enabled, dialog)
            if result is not None:
                enabled[:] = result
                self.populate_fields(enabled, field)
        fields_button.clicked.connect(edit_fields)
        choices = []
        for label, original in (('統計範圍', self.scope), ('顯示詞彙數量', self.limit),
                                ('點選動作', self.mode), ('排序', self.order)):
            layout.addWidget(QLabel(label))
            choice = QComboBox(dialog)
            choice.setAccessibleName(label)
            for index in range(original.count()):
                choice.addItem(original.itemText(index))
            choice.setCurrentIndex(original.currentIndex())
            layout.addWidget(choice)
            choices.append((original, choice))
        layout.addWidget(QLabel('顯示模式'))
        display_mode = QComboBox(dialog)
        display_mode.setObjectName('tag_cloud_display_mode')
        display_mode.setAccessibleName('顯示模式')
        display_mode.addItems(['側欄', '浮動視窗'])
        display_mode.setCurrentIndex(1 if self.action.display_mode() == 'floating' else 0)
        layout.addWidget(display_mode)
        shortcuts = QPushButton('套用並設定快捷鍵…', dialog)
        layout.addWidget(shortcuts)
        open_shortcuts = False
        def edit_shortcuts():
            nonlocal open_shortcuts
            open_shortcuts = True
            dialog.accept()
        shortcuts.clicked.connect(edit_shortcuts)
        random_colors = QCheckBox('隨機指定每個詞的字體顏色（同一詞保持固定）', dialog)
        random_colors.setChecked(prefs['random_colors'])
        layout.addWidget(random_colors)
        layout.addWidget(QLabel('候選顏色：點選色塊修改；未勾隨機時統一使用第一色。'))
        colors = list(prefs['colors'])
        row = QHBoxLayout()
        for index, color in enumerate(colors):
            button = QPushButton(color, dialog)
            button.setStyleSheet('border-bottom: 6px solid ' + color)
            button.setAccessibleName('候選顏色 ' + str(index + 1))
            def choose(checked=False, i=index, b=button):
                chosen = QColorDialog.getColor(QColor(colors[i]), dialog, '選擇字體顏色')
                if chosen.isValid():
                    colors[i] = chosen.name()
                    b.setText(chosen.name())
                    b.setStyleSheet('border-bottom: 6px solid ' + chosen.name())
            button.clicked.connect(choose)
            row.addWidget(button)
        layout.addLayout(row)
        summary = QLabel(self.status.text(), dialog)
        summary.setWordWrap(True)
        layout.addWidget(summary)
        clear = QCheckBox('清除目前選取（按確定後生效）', dialog)
        layout.addWidget(clear)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            prefs['random_colors'] = random_colors.isChecked()
            prefs['colors'] = colors
            chosen = field.currentData()
            if chosen != self.field.currentData():
                self.clear()
            self.save_enabled_fields(enabled)
            self.populate_fields()
            self.field.setCurrentIndex(self.field.findData(chosen))
            prefs['field'] = chosen
            for original, choice in choices:
                original.setCurrentIndex(choice.currentIndex())
            if clear.isChecked():
                self.clear()
            self.reload()
            self.action.set_display_mode('floating' if display_mode.currentIndex() == 1 else 'sidebar')
            if open_shortcuts:
                QTimer.singleShot(0, self.action.configure_cloud_shortcut)

    def reload(self, *args):
        try:
            db = self.action.gui.current_db
            key = self.field.currentData()
            if key is None:
                self.counts, self.term_books = [], {}
                self.render()
                return
            # Empty search respects the virtual library, without the current search.
            ids = (db.search_getting_ids('', '') if self.scope.currentIndex() == 0
                   else db.new_api.all_book_ids())
            self.book_ids = frozenset(ids)
            self.category_order = {}
            if key == 'id':
                values = {book_id: book_id for book_id in self.book_ids}
            elif key in db.new_api.fields:
                values = db.new_api.all_field_for(key, self.book_ids)
            else:
                values = {book_id: db.new_api.get_proxy_metadata(book_id).get(key) for book_id in self.book_ids}
            datatype = 'comments' if key == 'comments' else db.new_api.field_metadata[key]['datatype']
            self.counts, self.term_books = indexed_terms(values, datatype)
            prefs['scope'] = self.scope.currentIndex()
            self.render()
        except Exception as err:
            self.cloud.setPlainText('無法讀取標籤，請按重新整理。')
            self.status.setText(str(err))

    def render(self, *args):
        text = self.limit.currentText()
        prefs['limit'] = text if text == '全部' else int(text)
        needle = self.find.text().casefold().strip()
        values = [(name, count) for name, count in self.counts if needle in name.casefold()]
        if self.order.currentIndex() == 0 and self.field.currentData() is not None:
            key = (config['sort_tags_by'], self.field.currentData())
            if key not in self.category_order:
                categories = self.action.gui.current_db.new_api.get_categories(sort=key[0], book_ids=self.book_ids)
                self.category_order[key] = {tag.name: index for index, tag in enumerate(categories.get(key[1], ()))}
            positions = self.category_order[key]
            values.sort(key=lambda item: (positions.get(item[0], len(positions)), sort_key(item[0])))
        if text != '全部':
            values = values[:int(text)]
        if self.order.currentIndex() == 1:
            random.Random(self.order_seed).shuffle(values)
        counts = dict(self.counts)
        pinned = [(name, counts.get(name, 0)) for name in self.selected]
        values = [(name, count) for name, count in values if name not in self.selected]
        if text != '全部':
            values = values[:max(0, int(text) - len(pinned))]
        values = pinned + values
        self.names = [name for name, count in values]
        maximum = max((count for name, count in values), default=1)
        minimum = min((count for name, count in values), default=1)
        pieces = []
        for index, (name, count) in enumerate(values):
            colors = prefs['colors']
            slot = int.from_bytes(hashlib.sha256(name.encode('utf-8')).digest()[:4], 'big')
            color = colors[slot % len(colors)] if prefs['random_colors'] else colors[0]
            weight = 'bold' if name in self.selected else 'normal'
            mark = '✓ ' if name in self.selected else ''
            pieces.append(f'<a href="tag:{index}" title="{escape(name, quote=True)} · {count} 本" '
                          f'style="color:{color};font-size:{font_size(count, maximum, minimum)}pt;'
                          f'font-weight:{weight};text-decoration:none">'
                          f'{escape(mark + name).replace(" ", "&nbsp;")}</a>')
        self.cloud.setHtml('<p style="line-height:115%;margin:0;text-align:center">' +
                           ' &nbsp; '.join(pieces) + '</p>' if pieces else '沒有符合的標籤。')
        self.status.setText('已選：' + '、'.join(self.selected) if self.selected
                            else f'{len(self.counts)} 個詞彙；顯示 {len(values)} 個')

    def clicked(self, url):
        name = self.names[int(url.path())]
        if name in self.selected:
            self.selected.remove(name)
        elif self.mode.currentIndex() == 1:
            self.selected = [name]
        else:
            self.selected.append(name)
        self.apply_search()
        self.render()

    def change_click_mode(self, *args):
        prefs['click_mode'] = 'single' if self.mode.currentIndex() == 1 else 'intersection'
        if self.mode.currentIndex() == 1:
            self.selected = self.selected[-1:]
        self.apply_search()
        self.render()

    def apply_search(self, *args):
        search = self.action.gui.search
        current = str(search.currentText())
        if not self.selected:
            if self.last_query is not None and current == self.last_query:
                search.set_search_string(self.base_query or '')
            self.base_query = self.last_query = None
            return
        if self.last_query is None or current != self.last_query:
            self.base_query = current
        field = self.field.currentData()
        if field in ('tags', 'authors', 'series', 'publisher') or (field and field.startswith('#') and
                self.action.gui.current_db.new_api.field_metadata[field]['datatype'] in ('text', 'series')):
            query = tag_query(self.selected, True, field)
        else:
            matches = set.intersection(*(self.term_books.get(term, set()) for term in self.selected))
            query = book_query(matches)
        if self.base_query:
            query = '(' + self.base_query + ') and (' + query + ')'
        self.last_query = query
        search.set_search_string(query)

    def clear(self):
        self.selected = []
        self.apply_search()
        self.render()

    def reset_library(self):
        self.selected = []
        self.base_query = self.last_query = None
        self.populate_fields()
        self.find.blockSignals(True)
        self.find.setText('')
        self.find.blockSignals(False)
        self.reload()


class TagCloudAction(InterfaceAction):
    name = 'Tag Cloud'
    action_spec = ('標籤雲', None, '顯示或隱藏左側標籤雲', None)
    dont_add_to = frozenset(('toolbar', 'toolbar-device', 'toolbar-child', 'menubar',
                             'menubar-device', 'context-menu', 'context-menu-device',
                             'context-menu-split', 'context-menu-cover-browser', 'searchbar'))

    def genesis(self):
        self.panel = None
        self.qaction.setVisible(False)
        self.qaction.setIcon(QIcon.ic('tags.png'))
        self.qaction.setCheckable(True)
        self.qaction.toggled.connect(self.toggle)
        self.floating_action = QAction('顯示／隱藏標籤雲', self.gui)
        self.floating_action.setShortcutContext(Qt.ShortcutContext.ApplicationShortcut)
        self.gui.addAction(self.floating_action)
        self.floating_action.triggered.connect(self.toggle_cloud)
        self.gui.keyboard.register_shortcut('tag_cloud_toggle_floating', '顯示／隱藏標籤雲',
                                           default_keys=(), action=self.floating_action, group='Tag Cloud')

    def initialization_complete(self):
        try:
            view = self.gui.tags_view
            host = view.parentWidget()
            layout = host.layout()
            if layout is None or layout.indexOf(view) < 0:
                raise RuntimeError('目前分類樹結構不支援嵌入標籤雲。')
            self.panel = CloudPanel(self)
            self.splitter = QSplitter(Qt.Orientation.Vertical, host)
            layout.replaceWidget(view, self.splitter)
            self.tree_pane = QWidget(self.splitter)
            tree_layout = QVBoxLayout(self.tree_pane)
            tree_layout.setContentsMargins(0, 0, 0, 0)
            tree_layout.setSpacing(0)
            tree_layout.addWidget(view)
            bar = getattr(host, 'tb_bar', None)
            if bar is not None:
                layout.removeWidget(bar)
                tree_layout.addWidget(bar)
            self.splitter.addWidget(self.tree_pane)
            self.splitter.addWidget(self.panel)
            self.splitter.setCollapsible(0, False)
            self.splitter.setCollapsible(1, False)
            self.splitter.setSizes(prefs['sizes'])
            self.splitter.splitterMoved.connect(self.save_sizes)
            self.timer = QTimer(self.panel)
            self.timer.setSingleShot(True)
            self.timer.setInterval(250)
            self.timer.timeout.connect(self.panel.reload)
            self.gui.library_view.model().count_changed_signal.connect(self.schedule_reload)
            self.qaction.setChecked(prefs['visible'])
            self.panel.setVisible(prefs['visible'])
            self.panel.reload()
            if hasattr(self.gui, 'layout_container'):
                from calibre_plugins.tag_cloud.sidebar import Sidebar
                self.sidebar = Sidebar(self)
                self.sidebar.relayout()
                self.gui.tags_view.model().modelReset.connect(self.schedule_reload)
                changed = False
                for key in ('toolbar', 'toolbar-device', 'toolbar-child', 'menubar',
                            'menubar-device', 'searchbar', 'context-menu', 'context-menu-device',
                            'context-menu-cover-browser', 'context-menu-split'):
                    key = 'action-layout-' + key
                    items = gprefs.get(key)
                    if items and self.name in items:
                        gprefs[key] = tuple(item for item in items if item != self.name)
                        changed = True
                if changed:
                    self.gui.bars_manager.apply_settings()
            from calibre_plugins.tag_cloud.floating import Presentation
            self.presentation = Presentation(self, prefs)
        except Exception as err:
            self.qaction.setEnabled(False)
            error_dialog(self.gui, '標籤雲', '無法建立側欄標籤雲。', det_msg=str(err), show=True)

    def schedule_reload(self, *args):
        self.timer.start()

    def save_sizes(self, *args):
        if self.panel.parentWidget() is self.splitter and self.panel.isVisible() and not self.tree_pane.isHidden():
            prefs['sizes'] = self.splitter.sizes()

    def toggle(self, visible):
        prefs['visible'] = visible
        if self.panel is not None:
            if hasattr(self, 'presentation'):
                self.presentation.update_visibility()
            else:
                self.panel.setVisible(visible)
            if visible:
                self.panel.reload()
            if hasattr(self, 'sidebar'):
                self.sidebar.relayout()
                if visible and self.display_mode() == 'sidebar' and not self.tree_pane.isHidden():
                    self.splitter.setSizes(prefs['sizes'])

    def display_mode(self):
        return prefs['display_mode']

    def set_display_mode(self, mode):
        self.presentation.set_mode(mode)

    def toggle_cloud(self, *args):
        if hasattr(self, 'presentation'):
            self.presentation.toggle_cloud()

    def configure_cloud_shortcut(self):
        self.gui.iactions['Preferences'].do_config(initial_plugin=('Advanced', 'Keyboard'), close_after_initial=True)

    def shutting_down(self):
        if hasattr(self, 'presentation'):
            self.presentation.shutdown()
        return True

    def library_changed(self, db):
        if self.panel is not None:
            self.panel.reset_library()
