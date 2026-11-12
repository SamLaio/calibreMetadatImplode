from qt.core import (QAbstractButton, QAbstractItemView, QAction, QGroupBox, QLabel,
                     QLineEdit, QMainWindow, QMenu, QPlainTextEdit, QTextEdit, QToolButton, QWidget)
from calibre_plugins.traditional_chinese_supplement.strings import COMMON, SCOPES
from calibre_plugins.traditional_chinese_supplement.editor_strings import EDITOR_SCOPE, EDITOR_TEXT
from pathlib import Path
import sys


def scope_for(widget):
    node = widget
    while isinstance(node, QWidget):
        if isinstance(node, (QAbstractItemView, QLineEdit, QPlainTextEdit, QTextEdit)):
            return None
        module = type(node).__module__
        if module == 'config':
            archive = getattr(getattr(sys.modules.get(module), '__loader__', None), 'archive', '')
            if Path(archive).name == 'DeDRM.zip':
                return 'dedrm'
        for scope in SCOPES:
            prefix = scope if scope.startswith('calibre.') else 'calibre_plugins.' + scope
            if module == prefix or module.startswith(prefix + '.'):
                return scope
        node = node.parentWidget()
    return None


def translate_widget(widget):
    if not isinstance(widget, QWidget):
        return
    scope = scope_for(widget)
    if scope is None:
        return
    texts = SCOPES[scope]
    def translated(text):
        if scope == EDITOR_SCOPE and text in SCOPES['calibre.gui2']:
            return SCOPES['calibre.gui2'][text]
        return texts.get(text, COMMON.get(text, text))
    for getter, setter in (('toolTip', 'setToolTip'), ('statusTip', 'setStatusTip'), ('whatsThis', 'setWhatsThis')):
        old = getattr(widget, getter)()
        new = translated(old)
        if new != old:
            getattr(widget, setter)(new)
    if scope == EDITOR_SCOPE:
        if isinstance(widget, QMainWindow):
            for action in widget.findChildren(QAction):
                for getter, setter in ((action.text, action.setText), (action.toolTip, action.setToolTip),
                                       (action.statusTip, action.setStatusTip)):
                    old = getter()
                    new = EDITOR_TEXT.get(old, old)
                    if new != old:
                        setter(new)
        elif isinstance(widget, QMenu):
            old = widget.title()
            new = EDITOR_TEXT.get(old, old)
            if new != old:
                widget.setTitle(new)
    # Combo/list/table values can be program identifiers; never change their models.
    if isinstance(widget, (QLabel, QAbstractButton)) and not isinstance(widget, QToolButton):
        old = widget.text()
        new = translated(old)
        if scope == 'dedrm':
            new = new.replace('>Plugin Help</a>', '>外掛說明</a>')
        if new != old:
            widget.setText(new)
    elif isinstance(widget, QGroupBox):
        old = widget.title()
        new = translated(old)
        if new != old:
            widget.setTitle(new)
