from qt.core import QApplication, QCheckBox, QComboBox, QEvent, QGroupBox, QLabel, QObject, QSignalBlocker, QWidget
from calibre.gui2.actions import InterfaceAction
from calibre.gui2.actions.polish import Polish
from calibre.utils.localization import get_lang
from calibre_plugins.traditional_chinese_supplement.display import translate_widget
import traceback


# Match the original English too, so upstream Chinese translations take precedence.
LABELS = {
    'subset': ('Su&bset all embedded fonts', '將所有內嵌字型子集化(&B)'),
    'do_cover': ('Update the co&ver in the book files', '更新書檔中的封面(&V)'),
    'remove_jacket': ('Remove a previously inserted book jac&ket', '移除先前插入的書籍簡介頁(&K)'),
    'compress_images': ('Losslessly compress &images', '無損壓縮圖片(&I)'),
    'download_external_resources': ('&Download external resources', '下載外部資源(&D)'),
    'add_soft_hyphens': ('Add soft &hyphens', '加入軟連字號(&H)'),
    'remove_soft_hyphens': ('Remove soft h&yphens', '移除軟連字號(&Y)'),
    'upgrade_book': ('Up&grade book internals', '升級書籍內部結構(&G)'),
}
HEADINGS = {
    'Subsetting fonts': '字型子集化',
    'Update cover': '更新封面',
    'Remove book jacket': '移除書籍簡介頁',
    'Losslessly compress images': '無損壓縮圖片',
    'Download external resources': '下載外部資源',
    'Add soft-hyphens': '加入軟連字號',
    'Remove soft-hyphens': '移除軟連字號',
    'Upgrade book': '升級書籍內部結構',
}
DOWNLOAD_HELP = (
    '<p>Download external resources such as images, stylesheets, etc. that point to URLs instead of files in the book.\n'
    'All such resources will be downloaded and added to the book so that the book no longer references any external resources.\n'
    '</p>\n'
)
DOWNLOAD_HELP_ZH = (
    '<p>下載圖片、樣式表等以網址連結的外部資源，並加入書檔，'
    '讓書籍不再依賴這些外部資源。</p>\n'
)


def translate_polish(dialog):
    for name, (english, chinese) in LABELS.items():
        checkbox = getattr(dialog, 'opt_' + name, None)
        if isinstance(checkbox, QCheckBox) and checkbox.text().replace('&', '') == english.replace('&', ''):
            checkbox.setText(chinese)
    for name in LABELS:
        old = dialog.help_text.get(name, '')
        new = old
        for english, chinese in HEADINGS.items():
            new = new.replace('<h3>' + english + '</h3>', '<h3>' + chinese + '</h3>')
        if name == 'download_external_resources':
            new = new.replace(DOWNLOAD_HELP, DOWNLOAD_HELP_ZH)
        if new != old:
            dialog.help_text[name] = new
            if dialog.help_label.text() == old:
                dialog.help_label.setText(new)


KFX_TEXT = {
    'Options:': '選項：',
    "Show 'From KFX' completion popup:": '顯示「From KFX」轉換完成通知：',
    'Only on conversion error': '僅在轉換錯誤時',
    'Always': '一律顯示',
    'Never': '永不顯示',
    'Split landscape images when converting comics to PDF': '漫畫轉換為 PDF 時拆分橫向圖片',
    'Desaturate colors when converting Scribe Colorsoft notebooks': '轉換 Scribe Colorsoft 筆記本時降低色彩飽和度',
    "Select whether or not a notification popup will be shown upon completion of a 'From KFX' conversion job.":
        '選擇「From KFX」轉換工作完成後是否顯示通知視窗。',
    'Causes landscape orientation images in comics to be split into separate left and right side images\n'
    'when converting to PDF format. This is intended to break page spreads into individual page\n'
    'images. This option only applies to conversion done using the plugin CLI or From KFX GUI, not\n'
    "conversion using calibre's Convert Books feature.":
        '轉換為 PDF 時，將漫畫的橫向跨頁圖片拆分為左、右兩張單頁圖片。\n'
        '只適用於此外掛的命令列或 From KFX 介面，不適用於 calibre 的「轉換書本」功能。',
    'Mute the colors in Scribe notebooks to better match the files produced by Amazon when exporting them as PDF.':
        '降低 Scribe 筆記本的色彩飽和度，使結果更接近 Amazon 匯出的 PDF。',
}


def is_kfx_config(widget):
    return (isinstance(widget, QWidget) and type(widget).__module__ == 'calibre_plugins.kfx_input.config'
            and type(widget).__name__ == 'ConfigWidget')


def translate_kfx(widget):
    for child in widget.findChildren(QWidget):
        if isinstance(child, (QLabel, QCheckBox)):
            text = child.text()
            if text in KFX_TEXT:
                child.setText(KFX_TEXT[text])
        elif isinstance(child, QGroupBox):
            text = child.title()
            if text in KFX_TEXT:
                child.setTitle(KFX_TEXT[text])
        tip = child.toolTip()
        if tip in KFX_TEXT:
            child.setToolTip(KFX_TEXT[tip])
    combo = getattr(widget, 'ShowCompletionPopup', None)
    if isinstance(combo, QComboBox):
        with QSignalBlocker(combo):
            for index in range(combo.count()):
                text = combo.itemText(index)
                if text in KFX_TEXT:
                    combo.setItemText(index, KFX_TEXT[text])


def translate_window(widget):
    if isinstance(widget, Polish):
        translate_polish(widget)
    elif is_kfx_config(widget):
        translate_kfx(widget)
    else:
        translate_widget(widget)


class TranslationFilter(QObject):
    def start(self):
        self.failures = set()
        self.active = get_lang().lower().replace('-', '_') in ('zh_tw', 'zh_hant', 'zh_hant_tw')
        if self.active:
            app = QApplication.instance()
            app.installEventFilter(self)
            for widget in app.allWidgets():
                self.translate_safely(widget)

    def translate_safely(self, widget):
        try:
            translate_window(widget)
        except Exception as error:
            failure = (type(widget).__name__, type(error).__name__)
            if failure not in self.failures:
                self.failures.add(failure)
                print('正體中文補強：略過無法處理的元件', failure)
                traceback.print_exc()

    def stop(self):
        self.active = False
        app = QApplication.instance()
        if app is not None:
            app.removeEventFilter(self)

    def eventFilter(self, watched, event):
        if self.active and event.type() == QEvent.Type.Show:
            self.translate_safely(watched)
        return False


class TranslationAction(InterfaceAction):
    name = 'Traditional Chinese Supplement'
    action_spec = ('正體中文補強', None, '補齊已支援視窗的正體中文顯示文字', None)
    action_type = 'global'
    dont_add_to = frozenset(('toolbar', 'toolbar-device', 'toolbar-child', 'menubar',
                             'menubar-device', 'context-menu', 'context-menu-device',
                             'context-menu-split', 'context-menu-cover-browser', 'searchbar'))

    def genesis(self):
        self.qaction.setVisible(False)
        self.translator = None

    def initialization_complete(self):
        self.translator = TranslationFilter(self.gui)
        self.translator.start()

    def shutting_down(self):
        if self.translator is not None:
            self.translator.stop()
        return True
