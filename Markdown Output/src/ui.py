try:
    from qt.core import QCheckBox, QComboBox, QFormLayout, QLineEdit, QSpinBox
except ImportError:
    from PyQt5.Qt import QCheckBox, QComboBox, QFormLayout, QLineEdit, QSpinBox
from calibre.gui2.convert import Widget


OPTIONS = (
    'newline', 'max_line_length', 'force_max_line_length', 'inline_toc',
    'keep_links', 'keep_image_references', 'txt_output_encoding',
)


class PluginWidget(Widget):
    TITLE = 'Markdown 輸出'
    HELP = 'Markdown 輸出的換行、編碼、連結與圖片參照設定'
    COMMIT_NAME = 'Markdown_output'

    def setupUi(self, widget):
        layout = QFormLayout(widget)
        self.opt_newline = QComboBox(widget)
        layout.addRow('換行格式：', self.opt_newline)
        self.opt_max_line_length = QSpinBox(widget)
        self.opt_max_line_length.setRange(0, 2147483647)
        self.opt_max_line_length.setSpecialValueText('不限制')
        layout.addRow('每行最多字元：', self.opt_max_line_length)
        for name, label in (
            ('force_max_line_length', '沒有空白時也強制換行'),
            ('inline_toc', '在書籍開頭加入目錄'),
            ('keep_links', '保留連結'),
            ('keep_image_references', '保留圖片參照'),
        ):
            control = QCheckBox(label, widget)
            setattr(self, 'opt_' + name, control)
            layout.addRow(control)
        self.opt_txt_output_encoding = QLineEdit(widget)
        layout.addRow('輸出字元編碼：', self.opt_txt_output_encoding)

    def __init__(self, parent, get_option, get_help, db=None, book_id=None):
        Widget.__init__(self, parent, OPTIONS)
        self.db, self.book_id = db, book_id
        self.opt_newline.addItems(list(get_option('newline').option.choices))
        self.initialize_options(get_option, get_help, db, book_id)
