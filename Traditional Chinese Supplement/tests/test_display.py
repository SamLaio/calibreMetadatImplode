import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_translation import TranslationTests, ROOT, plugin, ui
from calibre_plugins.traditional_chinese_supplement import display
from calibre_plugins.traditional_chinese_supplement.strings import COMMON, SCOPES
from qt.core import (QAbstractButton, QAction, QApplication, QCheckBox, QComboBox, QEvent, QGroupBox,
                     QLabel, QLineEdit, QMainWindow, QSpinBox, QTableWidget, QWidget)


class DisplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        TranslationTests.setUpClass()
        cls.app = TranslationTests.app

    def setUp(self):
        self.windows = []

    def tearDown(self):
        for widget in self.windows:
            widget.close()
            widget.deleteLater()
        self.app.processEvents()

    def root(self, scope):
        module = scope if scope.startswith('calibre.') else 'calibre_plugins.' + scope + '.config'
        cls = type('ConfigWidget', (QWidget,), {'__module__': module})
        widget = cls()
        self.windows.append(widget)
        return widget

    def test_every_dictionary_entry_is_scoped_and_idempotent(self):
        for scope, texts in SCOPES.items():
            root = self.root(scope)
            for source, target in {**COMMON, **texts}.items():
                with self.subTest(scope=scope, source=source):
                    label = QLabel(source, root)
                    display.translate_widget(label)
                    self.assertEqual(label.text(), target)
                    display.translate_widget(label)
                    self.assertEqual(label.text(), target)
                    label.deleteLater()

    def test_semantic_values_and_business_signals_are_unchanged(self):
        root = self.root('goodreads')
        combo = QComboBox(root)
        combo.addItem('Add genre mapping', 'internal-id')
        combo.addItem('Options:', 'other-id')
        combo.setCurrentIndex(1)
        combo_changed = Mock()
        combo.currentIndexChanged.connect(combo_changed)
        edit = QLineEdit('Add genre mapping', root)
        changed = Mock()
        edit.textChanged.connect(changed)
        check = QCheckBox('Use first published date', root)
        check.setChecked(True)
        toggled = Mock()
        clicked = Mock()
        check.toggled.connect(toggled)
        check.clicked.connect(clicked)
        spin = QSpinBox(root)
        spin.setValue(37)
        action = QAction('Add genre mapping', root)
        action.setData('untranslated-action-key')
        for widget in root.findChildren(QWidget):
            display.translate_widget(widget)
        self.assertEqual(combo.currentIndex(), 1)
        self.assertEqual([combo.itemText(i) for i in range(2)], ['Add genre mapping', 'Options:'])
        self.assertEqual([combo.itemData(i) for i in range(2)], ['internal-id', 'other-id'])
        self.assertEqual(edit.text(), 'Add genre mapping')
        self.assertEqual(spin.value(), 37)
        self.assertTrue(check.isChecked())
        self.assertEqual(action.data(), 'untranslated-action-key')
        combo_changed.assert_not_called()
        changed.assert_not_called()
        toggled.assert_not_called()
        clicked.assert_not_called()
        check.click()
        clicked.assert_called_once()
        self.assertFalse(check.isChecked())

    def test_table_cells_unknown_and_other_plugins_are_untouched(self):
        root = self.root('goodreads')
        table = QTableWidget(1, 1, root)
        label = QLabel('Add genre mapping')
        table.setCellWidget(0, 0, label)
        display.translate_widget(label)
        self.assertEqual(label.text(), 'Add genre mapping')
        other = self.root('unrelated')
        unknown = QLabel('Add genre mapping', other)
        display.translate_widget(unknown)
        self.assertEqual(unknown.text(), 'Add genre mapping')
        chinese = QLabel('既有中文', root)
        display.translate_widget(chinese)
        self.assertEqual(chinese.text(), '既有中文')

    def test_group_title_tooltip_and_layout_change(self):
        root = self.root('goodreads')
        group = QGroupBox('Options:', root)
        label = QLabel('Get ASIN for kindle editions', group)
        label.setToolTip('Add genre mapping')
        display.translate_widget(group)
        display.translate_widget(label)
        self.assertEqual(group.title(), '選項：')
        self.assertIn('ASIN', label.text())
        self.assertEqual(label.toolTip(), '新增類型對應')

    def test_filter_catches_failure_instead_of_escaping_qt(self):
        root = self.root('goodreads')
        translator = ui.TranslationFilter()
        with patch.object(ui, 'get_lang', return_value='zh_TW'):
            translator.start()
        try:
            with patch.object(ui, 'translate_window', side_effect=RuntimeError('test failure')), patch.object(ui.traceback, 'print_exc') as log:
                QApplication.sendEvent(root, QEvent(QEvent.Type.Show))
                log.assert_called_once()
            self.assertIn(('ConfigWidget', 'RuntimeError'), translator.failures)
        finally:
            translator.stop()

    def test_real_metadata_window_and_library_remain_unchanged(self):
        import tempfile
        from calibre.db.legacy import LibraryDatabase
        from calibre.ebooks.metadata.book.base import Metadata
        from calibre.gui2.metadata.single import MetadataSingleDialog
        with tempfile.TemporaryDirectory(dir=ROOT / 'dist') as folder:
            db = LibraryDatabase(folder)
            book_id = db.create_book_entry(Metadata('Data files', ['Test Author']))
            before = db.get_metadata(book_id, index_is_id=True).title
            dialog = MetadataSingleDialog(db)
            self.windows.append(dialog)
            labels = [x for x in dialog.findChildren(QWidget) if isinstance(x, (QLabel, QAbstractButton)) and x.text() == 'Data files']
            self.assertTrue(labels, 'Expected the real metadata Data files button')
            for child in [dialog] + dialog.findChildren(QWidget):
                display.translate_widget(child)
            for label in labels:
                self.assertEqual(label.text(), '資料檔案')
            self.assertEqual(db.get_metadata(book_id, index_is_id=True).title, before)
            dialog.deleteLater()
            self.windows.remove(dialog)
            self.app.processEvents()
            db.close()

    def test_main_action_is_hidden_but_translation_starts(self):
        gui = QMainWindow()
        self.windows.append(gui)
        action = ui.TranslationAction(gui, None)
        action.qaction = QAction('正體中文補強', gui)
        action.genesis()
        self.assertFalse(action.qaction.isVisible())
        self.assertIn('toolbar', action.dont_add_to)
        with patch.object(ui, 'get_lang', return_value='zh_TW'):
            action.initialization_complete()
        self.assertTrue(action.translator.active)
        action.shutting_down()

    def test_same_archive_supports_main_gui_and_editor(self):
        from calibre.customize import EditBookToolPlugin, InterfaceActionBase
        from calibre.gui2.tweak_book import plugin as editor_plugin
        self.assertTrue(issubclass(type(plugin.TraditionalChineseSupplement(None)), InterfaceActionBase))
        self.assertTrue(issubclass(plugin.TraditionalChineseSupplement, EditBookToolPlugin))
        base = plugin.TraditionalChineseSupplement(None)
        tools = list(editor_plugin.load_plugin_tools(base))
        self.assertEqual(len(tools), 1)
        self.assertFalse(tools[0].allowed_in_toolbar)
        self.assertFalse(tools[0].allowed_in_menu)
        self.assertTrue(tools[0].translator.active)
        gui = QMainWindow()
        self.windows.append(gui)
        tool = tools[0]
        with patch.object(editor_plugin, 'get_boss', return_value=SimpleNamespace(gui=gui)), patch.object(ui, 'get_lang', return_value='zh_TW'):
            first = tool.create_action(True)
            translator = tool.translator
            second = tool.create_action(False)
            self.assertIs(tool.translator, translator)
            self.assertTrue(translator.active)
            self.assertFalse(first.isVisible())
            self.assertFalse(second.isVisible())
            translator.stop()


if __name__ == '__main__':
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(DisplayTests))
    raise SystemExit(not result.wasSuccessful())
