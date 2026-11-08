from qt.core import QAction, QApplication
from calibre.gui2.tweak_book.plugin import Tool
from calibre_plugins.traditional_chinese_supplement.ui import TranslationFilter


class TranslationTool(Tool):
    name = 'traditional-chinese-supplement'
    allowed_in_toolbar = False
    allowed_in_menu = False

    def __init__(self):
        self.translator = TranslationFilter(QApplication.instance())
        self.translator.start()

    def create_action(self, for_toolbar=True):
        action = QAction(QApplication.instance())
        action.setVisible(False)
        return action
