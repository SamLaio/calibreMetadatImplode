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

plugin_class = loader.load(str(ROOT / 'dist/Hardcover Sync-zh_TW-release.zip'))
from calibre_plugins.hardcover_sync import config as cfg


class HardcoverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or Application([])

    def setUp(self):
        self.plugin = plugin_class(str(ROOT / 'dist/Hardcover Sync-zh_TW-release.zip'))
        self.network = patch('socket.socket.connect', side_effect=AssertionError('禁止測試連網'))
        self.network.start()
        self.widget = self.plugin.config_widget()

    def tearDown(self):
        self.widget.close()
        self.network.stop()

    def test_identity_translation_and_no_auto_push(self):
        self.assertEqual(self.plugin.version, (0, 4, 0, 1))
        self.assertEqual(self.plugin.name, 'Hardcover Sync')
        texts = [x.text() for x in self.widget.findChildren(QLabel)]
        self.assertIn('Hardcover API 金鑰：', texts)
        self.assertNotIn('Goodreads', self.plugin.actual_plugin)

    def test_api_key_rate_and_auto_push_roundtrip(self):
        self.widget.api_key.setText(' qa-token ')
        self.widget.requests_per_minute.setValue(17)
        self.widget.auto_push.setChecked(False)
        self.widget.save_settings()
        self.assertEqual(cfg.get_api_key(), 'qa-token')
        self.assertEqual(cfg.get_requests_per_minute(), 17)
        self.assertFalse(cfg.get_auto_push())
        again = self.plugin.config_widget()
        self.assertEqual(again.api_key.text(), 'qa-token')
        self.assertEqual(again.requests_per_minute.value(), 17)
        self.assertFalse(again.auto_push.isChecked())
        again.close()


if __name__ == '__main__':
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(HardcoverTests))
    raise SystemExit(not result.wasSuccessful())
