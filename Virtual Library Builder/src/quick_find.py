"""Quick metadata lookup using the existing calibre library search."""
import re
from qt.core import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton, QCheckBox, Qt
from calibre.gui2 import error_dialog
from calibre_plugins.virtual_library_builder import core


def find_fields(db):
    return {key: meta for key, meta in core.fields(db).items()
            if meta['datatype'] in {'text', 'series', 'enumeration'}}


def quick_query(metadata, field, text, exact=False):
    text = text.strip()
    if not text:
        raise ValueError('請輸入要尋找的內容。')
    def isbn_query():
        value = re.sub(r'[\s-]', '', text).upper()
        if not re.fullmatch(r'[0-9X]+', value):
            raise ValueError('ISBN 請輸入數字，可包含連字號與結尾 X。')
        return 'identifiers:' + core.quote('=isbn:' + ('=' if exact else '') + value)
    if field == 'isbn':
        return isbn_query()
    operator = 'eq' if exact else 'contains'
    if field != '*':
        if field not in metadata:
            raise ValueError('目前書庫沒有這個欄位。')
        return core.condition(field, metadata[field]['datatype'], operator, text)
    names = [key for key in ('authors', 'title', 'series', 'publisher') if key in metadata]
    for key, meta in metadata.items():
        label = (key + ' ' + str(meta.get('name') or '')).casefold()
        if any(word in label for word in ('翻譯', '譯者', 'translator', 'translate')) and key not in names:
            names.append(key)
    terms = [core.condition(key, metadata[key]['datatype'], operator, text) for key in names]
    if re.fullmatch(r'[0-9Xx\s-]+', text):
        terms.append(isbn_query())
    return core.expression(terms, any_match=True)


class QuickFind(QDialog):
    def __init__(self, gui):
        super().__init__(gui, Qt.WindowType.Window)
        self.gui = gui
        self.db = gui.current_db
        self.metadata = find_fields(self.db)
        self.setWindowTitle('快速尋找')
        self.setModal(False)
        self.setWindowModality(Qt.WindowModality.NonModal)
        self.resize(620, 190)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel('輸入作者、書名、ISBN、系列或翻譯者；搜尋保留目前虛擬書庫範圍。'))
        row = QHBoxLayout()
        self.field = QComboBox()
        self.field.setAccessibleName('尋找欄位')
        self.field.addItem('全部常用欄位', '*')
        for key in ('authors', 'title', 'isbn', 'series', 'publisher'):
            if key == 'isbn':
                self.field.addItem('ISBN', key)
            elif key in self.metadata:
                self.field.addItem(str(self.metadata[key].get('name') or key), key)
        for key, meta in self.metadata.items():
            if key not in ('authors', 'title', 'series', 'publisher'):
                self.field.addItem(str(meta.get('name') or key) + ' (' + key + ')', key)
        row.addWidget(self.field)
        self.text = QLineEdit()
        self.text.setAccessibleName('尋找內容')
        self.text.setPlaceholderText('輸入文字後按 Enter 搜尋…')
        self.text.setClearButtonEnabled(True)
        self.text.returnPressed.connect(self.search)
        row.addWidget(self.text, 1)
        search = QPushButton('搜尋')
        search.setAutoDefault(False)
        search.clicked.connect(self.search)
        row.addWidget(search)
        layout.addLayout(row)
        self.exact = QCheckBox('精確比對（預設為包含）')
        layout.addWidget(self.exact)
        self.status = QLabel('每次搜尋取代原搜尋列；不更動書目或虛擬書庫。')
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        bottom = QHBoxLayout()
        shortcut = QPushButton('快捷鍵設定…')
        shortcut.setAutoDefault(False)
        shortcut.clicked.connect(self.configure_shortcut)
        bottom.addWidget(shortcut)
        bottom.addStretch()
        close = QPushButton('關閉')
        close.setAutoDefault(False)
        close.clicked.connect(self.close)
        bottom.addWidget(close)
        layout.addLayout(bottom)
        self.text.setFocus()

    def search(self):
        try:
            if self.gui.current_db is not self.db:
                raise ValueError('目前書庫已變更，請重新開啟快速尋找。')
            query = quick_query(self.metadata, self.field.currentData(), self.text.text(), self.exact.isChecked())
            self.db.new_api.search(query)
            self.gui.search.set_search_string(query)
            self.status.setText('已套用搜尋，可直接操作主書單或繼續尋找。')
        except Exception as err:
            error_dialog(self, '無法尋找', str(err), show=True)

    def configure_shortcut(self):
        self.gui.iactions['Preferences'].do_config(initial_plugin=('Advanced', 'Keyboard'), close_after_initial=True)
