from qt.core import (
    QComboBox, QHBoxLayout, QIcon, QLabel, QLineEdit, QPushButton,
    QSplitter, QTextBrowser, QTimer, QToolButton, QVBoxLayout, QWidget, Qt,
    QDialog, QDialogButtonBox, QCheckBox, QColor, QColorDialog,
)
from calibre.gui2 import error_dialog
from calibre.gui2.actions import InterfaceAction
from calibre.utils.config import JSONConfig
from calibre_plugins.tag_cloud.core import count_tags, font_size, tag_query
from html import escape
import hashlib
import random

prefs = JSONConfig('plugins/tag_cloud')
prefs.defaults.update(visible=True, sizes=[600, 300], limit=60, match_all=True, scope=0, field='tags')
prefs.defaults.update(random_colors=True, colors=['#56b4e9', '#e69f00', '#009e73', '#cc79a7', '#d55e00'])


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
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)
        header = QHBoxLayout()
        header.addWidget(QLabel('標籤雲 0.1.1'))
        header.addStretch()
        refresh = QToolButton(self)
        refresh.setText('更新')
        refresh.setToolTip('重新統計標籤')
        refresh.clicked.connect(self.reload)
        header.addWidget(refresh)
        settings = QToolButton(self)
        settings.setText('設定')
        settings.setToolTip('設定欄位與字體顏色')
        settings.clicked.connect(self.configure)
        header.addWidget(settings)
        close = QToolButton(self)
        close.setText('×')
        close.setToolTip('隱藏標籤雲；可由工具列重新開啟')
        close.clicked.connect(lambda: action.qaction.setChecked(False))
        header.addWidget(close)
        layout.addLayout(header)
        self.field = QComboBox(self)
        self.field.setAccessibleName('統計欄位')
        layout.addWidget(self.field)
        self.populate_fields()
        options = QHBoxLayout()
        self.scope = QComboBox(self)
        self.scope.addItems(['目前虛擬書庫', '整個書庫'])
        self.scope.setCurrentIndex(prefs['scope'])
        self.scope.setAccessibleName('統計範圍')
        self.limit = QComboBox(self)
        self.limit.addItems(['40', '60', '100', '200'])
        self.limit.setCurrentText(str(prefs['limit']))
        self.limit.setAccessibleName('顯示標籤數量')
        options.addWidget(self.scope)
        options.addWidget(self.limit)
        layout.addLayout(options)
        self.find = QLineEdit(self)
        self.find.setPlaceholderText('搜尋標籤……')
        self.find.setClearButtonEnabled(True)
        self.find.setAccessibleName('搜尋標籤')
        layout.addWidget(self.find)
        self.cloud = QTextBrowser(self)
        self.cloud.setOpenLinks(False)
        self.cloud.setAccessibleName('標籤雲；點選標籤篩選書籍')
        self.cloud.anchorClicked.connect(self.clicked)
        layout.addWidget(self.cloud)
        self.status = QLabel(self)
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        footer = QHBoxLayout()
        self.mode = QComboBox(self)
        self.mode.addItems(['全部符合', '任一符合'])
        self.mode.setCurrentIndex(0 if prefs['match_all'] else 1)
        footer.addWidget(self.mode)
        clear = QPushButton('清除選取', self)
        clear.clicked.connect(self.clear)
        footer.addWidget(clear)
        layout.addLayout(footer)
        self.scope.currentIndexChanged.connect(self.reload)
        self.field.currentIndexChanged.connect(self.change_field)
        self.limit.currentIndexChanged.connect(self.render)
        self.find.textChanged.connect(self.render)
        self.mode.currentIndexChanged.connect(self.apply_search)

    def populate_fields(self):
        self.field.blockSignals(True)
        self.field.clear()
        for key, label in (('tags', '標籤'), ('series', '系列'), ('authors', '作者')):
            self.field.addItem(label, key)
        metadata = self.action.gui.current_db.new_api.field_metadata
        for key in sorted(metadata.custom_field_keys()):
            info = metadata[key]
            if info['datatype'] == 'series' or (info['datatype'] == 'text' and info['is_multiple']):
                self.field.addItem(info['name'] + ' (' + key + ')', key)
        index = self.field.findData(prefs['field'])
        self.field.setCurrentIndex(max(0, index))
        self.field.blockSignals(False)

    def change_field(self, *args):
        self.clear()
        prefs['field'] = self.field.currentData()
        self.reload()

    def configure(self):
        dialog = QDialog(self)
        dialog.setWindowTitle('Tag Cloud 0.1.1 — 設定')
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel('雲的統計與篩選欄位（標籤／系列／作者／自訂欄位）'))
        field = QComboBox(dialog)
        for index in range(self.field.count()):
            field.addItem(self.field.itemText(index), self.field.itemData(index))
        field.setCurrentIndex(self.field.currentIndex())
        layout.addWidget(field)
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
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            prefs['random_colors'] = random_colors.isChecked()
            prefs['colors'] = colors
            self.field.setCurrentIndex(field.currentIndex())
            self.render()

    def reload(self, *args):
        try:
            db = self.action.gui.current_db
            # Empty search respects the virtual library, without the current search.
            ids = (db.search_getting_ids('', '') if self.scope.currentIndex() == 0
                   else db.new_api.all_book_ids())
            self.counts = count_tags(db.new_api.all_field_for(self.field.currentData(), ids))
            prefs['scope'] = self.scope.currentIndex()
            self.render()
        except Exception as err:
            self.cloud.setPlainText('無法讀取標籤，請按重新整理。')
            self.status.setText(str(err))

    def render(self, *args):
        prefs['limit'] = int(self.limit.currentText())
        needle = self.find.text().casefold().strip()
        values = [(name, count) for name, count in self.counts if needle in name.casefold()]
        values = values[:prefs['limit']]
        random.Random(self.order_seed).shuffle(values)
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
                            else f'{len(self.counts)} 個標籤；顯示 {len(values)} 個')

    def clicked(self, url):
        name = self.names[int(url.path())]
        if name in self.selected:
            self.selected.remove(name)
        else:
            self.selected.append(name)
        self.apply_search()
        self.render()

    def apply_search(self, *args):
        prefs['match_all'] = self.mode.currentIndex() == 0
        search = self.action.gui.search
        current = str(search.currentText())
        if not self.selected:
            if self.last_query is not None and current == self.last_query:
                search.set_search_string(self.base_query or '')
            self.base_query = self.last_query = None
            return
        if self.last_query is None or current != self.last_query:
            self.base_query = current
        query = tag_query(self.selected, prefs['match_all'], self.field.currentData())
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
        self.find.clear()
        self.reload()


class TagCloudAction(InterfaceAction):
    name = 'Tag Cloud'
    action_spec = ('標籤雲', None, '顯示或隱藏左側標籤雲', None)

    def genesis(self):
        self.panel = None
        self.qaction.setIcon(QIcon.ic('tags.png'))
        self.qaction.setCheckable(True)
        self.qaction.toggled.connect(self.toggle)

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
            self.splitter.addWidget(view)
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
        except Exception as err:
            self.qaction.setEnabled(False)
            error_dialog(self.gui, '標籤雲', '無法建立側欄標籤雲。', det_msg=str(err), show=True)

    def schedule_reload(self, *args):
        self.timer.start()

    def save_sizes(self, *args):
        if self.panel.isVisible():
            prefs['sizes'] = self.splitter.sizes()

    def toggle(self, visible):
        prefs['visible'] = visible
        if self.panel is not None:
            self.panel.setVisible(visible)
            if visible:
                self.panel.reload()

    def library_changed(self, db):
        if self.panel is not None:
            self.panel.reset_library()
