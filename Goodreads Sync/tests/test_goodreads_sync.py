import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
from calibre.utils.config import config_dir
if (ROOT / 'dist').resolve() not in Path(config_dir).resolve().parents:
    raise SystemExit('請使用 dist 下的獨立 CALIBRE_CONFIG_DIRECTORY。')
from calibre.customize.zipplugin import loader
from calibre.gui2 import Application
from qt.core import QApplication, QCheckBox, QLabel, QLineEdit

from types import SimpleNamespace
from calibre.db.legacy import LibraryDatabase
from qt.core import QAction, QMainWindow
plugin_class = loader.load(str(ROOT / 'dist/Goodreads Sync-zh_TW-release.zip'))
from calibre_plugins.goodreads_sync import config as cfg


class GoodreadsSyncTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or Application([])
        cls.db = LibraryDatabase(str(ROOT / 'dist/gs-test-library'))

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def setUp(self):
        self.gui = QMainWindow()
        self.gui.current_db = self.db
        self.gui.must_restart_before_config = False
        model = SimpleNamespace(db=self.db, custom_columns={}, orig_headers={'rating': '評分'})
        self.gui.library_view = SimpleNamespace(model=lambda: model)
        self.gui.keyboard = Mock()
        self.gui.keyboard.shortcuts = {}
        self.plugin = plugin_class(str(ROOT / 'dist/Goodreads Sync-zh_TW-release.zip'))
        action = self.plugin.load_actual_plugin(self.gui)
        action.interface_action_base_plugin = self.plugin
        action.qaction = QAction('Goodreads Sync', self.gui)
        self.plugin.actual_plugin_ = action
        cfg.plugin_prefs[cfg.STORE_USERS] = {'測試使用者': {
            cfg.KEY_USER_ID: 'qa', cfg.KEY_USER_TOKEN: '', cfg.KEY_USER_SECRET: '', cfg.KEY_SHELVES: []}}
        self.network = patch('socket.socket.connect', side_effect=AssertionError('禁止測試連網'))
        self.network.start()
        self.widget = self.plugin.config_widget()

    def tearDown(self):
        self.widget.close()
        self.gui.close()
        self.network.stop()

    def test_version_and_direct_translation(self):
        self.assertEqual(self.plugin.version, (1, 17, 6, 1))
        self.assertEqual(cfg._('Select Goodreads user:'), '選擇 Goodreads 使用者：')
        labels = [x.text() for x in self.widget.findChildren(QLabel)]
        self.assertIn('選擇 Goodreads 使用者：', labels)
        self.assertNotIn('calibre_plugins.traditional_chinese_supplement.ui', sys.modules)

    def test_custom_column_helper_and_settings_roundtrip(self):
        helper = self.widget.get_create_new_custom_column_instance
        self.assertIsNotNone(helper)
        self.assertEqual(self.widget.get_custom_columns(['text']), {})
        self.widget.save_settings()
        first = cfg.plugin_prefs[cfg.STORE_USERS]
        self.widget.save_settings()
        self.assertEqual(cfg.plugin_prefs[cfg.STORE_USERS], first)
        self.assertIn('測試使用者', first)
        self.assertEqual(first['測試使用者'][cfg.KEY_USER_ID], 'qa')

    def test_translated_choice_labels_keep_internal_values(self):
        action = cfg.ActionTypeComboBox(self.widget, 'ADD')
        self.assertEqual(action.get_selected_action(), 'ADD')
        action.populate_combo('REMOVE')
        self.assertEqual(action.get_selected_action(), 'REMOVE')
        isbn = cfg.ISBNComboBox(self.widget, cfg.plugin_prefs[cfg.STORE_PLUGIN][cfg.KEY_UPDATE_ISBN])
        before = isbn.selected_value()
        self.assertEqual(isbn.selected_value(), before)
        self.assertEqual(cfg._('Add to shelf'), '加入書架')

    def test_real_hardcover_has_independent_identity(self):
        other_class = loader.load(str(ROOT / 'dist/Hardcover Sync-zh_TW-release.zip'))
        other = other_class(str(ROOT / 'dist/Hardcover Sync-zh_TW-release.zip'))
        self.assertNotEqual(other.name, self.plugin.name)
        self.assertIn('hardcover_sync', other.actual_plugin)
        self.assertIn('goodreads_sync', self.plugin.actual_plugin)
        self.assertNotEqual(other_class.__module__, plugin_class.__module__)


if __name__ == '__main__':
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(GoodreadsSyncTests))
    raise SystemExit(not result.wasSuccessful())
