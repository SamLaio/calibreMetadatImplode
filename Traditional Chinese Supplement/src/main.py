import builtins
import sys

from qt.core import QAction, QApplication
from calibre.utils import localization
from calibre.gui2.tweak_book.plugin import Tool
from calibre_plugins.traditional_chinese_supplement.ui import TranslationFilter
from calibre_plugins.traditional_chinese_supplement.editor_strings import EDITOR_SCOPE, EDITOR_TEXT


def install_editor_gettext():
    if getattr(localization._, '__module__', None) == __name__:
        return

    def for_editor(gettext):
        def translate(text, *args):
            translated = gettext(text, *args)
            if translated in (text, *args[:1]) and translated in EDITOR_TEXT:
                module = sys._getframe(1).f_globals.get('__name__', '')
                if module == EDITOR_SCOPE or module.startswith(EDITOR_SCOPE + '.'):
                    return EDITOR_TEXT[translated]
            return translated
        return translate

    for name in ('_', 'ngettext'):
        original = getattr(localization, name)
        wrapped = for_editor(original)
        setattr(localization, name, wrapped)
        setattr(builtins, name, for_editor(getattr(builtins, name)))
        # Modules imported before the editor tool retain their original gettext reference.
        for module_name, module in tuple(sys.modules.items()):
            if module_name.startswith(EDITOR_SCOPE + '.') and getattr(module, name, None) is original:
                setattr(module, name, wrapped)


class TranslationTool(Tool):
    name = 'traditional-chinese-supplement'
    allowed_in_toolbar = False
    allowed_in_menu = False

    def __init__(self):
        self.translator = TranslationFilter(QApplication.instance())
        self.translator.start()
        if self.translator.active:
            install_editor_gettext()

    def create_action(self, for_toolbar=True):
        action = QAction(QApplication.instance())
        action.setVisible(False)
        return action
