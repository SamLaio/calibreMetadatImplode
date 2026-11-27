import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.dont_write_bytecode = True
from qt.core import QAction, QApplication, QFrame, QMainWindow, QTreeView, QVBoxLayout, QLineEdit
from calibre.db.legacy import LibraryDatabase
from calibre.ebooks.metadata.book.base import Metadata

source = Path(__file__).parents[1] / 'src'
spec = importlib.util.spec_from_file_location('calibre_plugins.tag_cloud', source / '__init__.py',
                                            submodule_search_locations=[str(source)])
plugin = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = plugin
spec.loader.exec_module(plugin)
from calibre_plugins.tag_cloud import ui


class Search:
    def __init__(self):
        self.text = ''

    def currentText(self):
        return self.text

    def set_search_string(self, text):
        self.text = text


class GuiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        from calibre.utils.config import config_dir
        if not Path(config_dir).resolve().is_relative_to((Path(__file__).parents[2] / 'dist').resolve()):
            raise RuntimeError('測試僅能使用 dist 下的隔離設定。')
        self.temporary = tempfile.TemporaryDirectory(dir=Path(__file__).parents[2] / 'dist')
        self.db = LibraryDatabase(self.temporary.name)
        for title, tags, author, series in [('甲', ['歷史', '台灣'], '作者甲', '系列甲'),
                                           ('乙', ['歷史'], '作者乙', '系列甲'),
                                           ('丙', ['科幻'], '作者甲', None)]:
            mi = Metadata(title, [author])
            mi.tags, mi.series = tags, series
            self.db.create_book_entry(mi)
        self.gui = QMainWindow()
        self.gui.current_db = self.db
        self.gui.search = Search()
        self.gui.tags_view = QTreeView()
        host = QFrame(self.gui)
        self.gui.setCentralWidget(host)
        layout = QVBoxLayout(host)
        layout.addWidget(self.gui.tags_view)
        self.bottom = QLineEdit(host)
        layout.addWidget(self.bottom)
        # Exercise real Qt layout integration with an isolated database.
        from qt.core import QObject
        self.action = ui.TagCloudAction.__new__(ui.TagCloudAction)
        QObject.__init__(self.action)
        self.action.gui = self.gui
        self.action.qaction = QAction(self.gui)
        self.action.qaction.setCheckable(True)
        self.action.panel = None
        self.action.qaction.toggled.connect(self.action.toggle)
        class Signal:
            def connect(self, slot):
                pass
        self.gui.library_view = SimpleNamespace(model=lambda: SimpleNamespace(count_changed_signal=Signal()))
        ui.prefs['field'] = 'tags'
        ui.prefs['visible'] = True
        self.action.initialization_complete()

    def tearDown(self):
        self.gui.close()
        self.gui.deleteLater()
        self.app.processEvents()
        self.db.close()
        self.temporary.cleanup()

    def test_sidebar_and_field_search(self):
        panel = self.action.panel
        self.assertEqual(self.action.splitter.widget(0), self.gui.tags_view)
        self.assertEqual(self.action.splitter.parentWidget().layout().indexOf(self.bottom), 1)
        self.assertEqual(dict(panel.counts)['歷史'], 2)
        from qt.core import QUrl
        panel.clicked(QUrl('tag:' + str(panel.names.index('歷史'))))
        self.assertEqual(len(self.db.new_api.search(self.gui.search.text)), 2)
        panel.field.setCurrentIndex(panel.field.findData('authors'))
        self.assertEqual(self.gui.search.text, '')
        panel.clicked(QUrl('tag:' + str(panel.names.index('作者甲'))))
        self.assertEqual(len(self.db.new_api.search(self.gui.search.text)), 2)
        panel.field.setCurrentIndex(panel.field.findData('series'))
        self.assertEqual(panel.counts, [('系列甲', 2)])

    def test_search_restore_and_manual_edits(self):
        panel = self.action.panel
        self.gui.search.text = 'title:"=甲"'
        panel.selected = ['歷史']
        panel.apply_search()
        self.assertEqual(len(self.db.new_api.search(self.gui.search.text)), 1)
        panel.clear()
        self.assertEqual(self.gui.search.text, 'title:"=甲"')
        panel.selected = ['歷史']
        panel.apply_search()
        self.gui.search.text = 'title:"=乙"'
        panel.clear()
        self.assertEqual(self.gui.search.text, 'title:"=乙"')

    def test_render_and_library_reset(self):
        panel = self.action.panel
        self.gui.resize(500, 700)
        self.gui.show()
        self.app.processEvents()
        self.assertGreater(panel.cloud.viewport().width(), 0)
        self.assertIn('歷史', panel.cloud.toPlainText())
        panel.selected = ['歷史']
        panel.reset_library()
        self.assertEqual(panel.selected, [])
        self.assertEqual(panel.field.currentData(), 'tags')

    def test_settings_colors_and_field(self):
        from qt.core import QTimer, QDialog, QComboBox, QCheckBox
        panel = self.action.panel
        def accept():
            dialog = next(w for w in QApplication.topLevelWidgets() if isinstance(w, QDialog))
            field = dialog.findChild(QComboBox)
            field.setCurrentIndex(field.findData('authors'))
            dialog.findChild(QCheckBox).setChecked(False)
            dialog.accept()
        QTimer.singleShot(0, accept)
        panel.configure()
        self.assertEqual(panel.field.currentData(), 'authors')
        self.assertFalse(ui.prefs['random_colors'])
        self.assertIn(ui.prefs['colors'][0], panel.cloud.toHtml())

    def test_exact_special_names(self):
        from calibre_plugins.tag_cloud.core import tag_query
        for name in ['a"b', r'c\d', '.階層', '=等號', 'A & B']:
            mi = Metadata(name, [name])
            mi.tags = [name]
            self.db.create_book_entry(mi)
            self.assertEqual(len(self.db.new_api.search(tag_query([name]))), 1, name)

    def test_custom_fields_and_virtual_library(self):
        self.db.create_custom_column('cloud_tags', '自訂主題', 'text', True)
        self.db.create_custom_column('cloud_series', '自訂系列', 'series', False)
        self.db.close()
        self.db = LibraryDatabase(self.temporary.name)
        self.gui.current_db = self.db
        ids = list(self.db.new_api.all_book_ids())
        self.db.new_api.set_field('#cloud_tags', {ids[0]: ['自訂甲']})
        self.db.new_api.set_field('#cloud_series', {ids[1]: '自訂系列甲'})
        panel = self.action.panel
        panel.populate_fields()
        panel.field.setCurrentIndex(panel.field.findData('#cloud_tags'))
        self.assertEqual(panel.counts, [('自訂甲', 1)])
        panel.field.setCurrentIndex(panel.field.findData('#cloud_series'))
        self.assertEqual(panel.counts, [('自訂系列甲', 1)])
        self.db.data.set_base_restriction('tags:"=台灣"')
        panel.field.setCurrentIndex(panel.field.findData('tags'))
        panel.scope.setCurrentIndex(0)
        panel.reload()
        self.assertEqual(dict(panel.counts), {'歷史': 1, '台灣': 1})
        panel.scope.setCurrentIndex(1)
        self.assertEqual(dict(panel.counts)['歷史'], 2)


if __name__ == '__main__':
    result = unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(GuiTests))
    raise SystemExit(not result.wasSuccessful())
