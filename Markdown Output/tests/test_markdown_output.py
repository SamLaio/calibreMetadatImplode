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

from qt.core import QWidget
plugin_class = loader.load(str(ROOT / 'dist/Markdown Output-zh_TW-release.zip'))


class MarkdownTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or Application([])

    def setUp(self):
        self.plugin = plugin_class(str(ROOT / 'dist/Markdown Output-zh_TW-release.zip'))
        options = {x.option.name: x for x in self.plugin.options}
        self.widget = self.plugin.gui_configuration_widget(None, options.__getitem__, lambda key: '', None)

    def tearDown(self):
        self.widget.close()

    def test_independent_ui_and_translation(self):
        self.assertEqual(self.plugin.version, (1, 0, 3, 1))
        self.assertEqual(self.widget.TITLE, 'Markdown 輸出')
        self.assertFalse(hasattr(self.widget, 'gridLayout'))
        self.assertTrue(self.widget.opt_keep_links.isChecked())
        self.assertTrue(self.widget.opt_keep_image_references.isChecked())

    def test_option_keys_and_commit_roundtrip(self):
        self.widget.opt_newline.setCurrentText('unix')
        self.widget.opt_max_line_length.setValue(45)
        self.widget.opt_keep_links.setChecked(False)
        self.widget.opt_txt_output_encoding.setText('utf-8')
        result = self.widget.commit(save_defaults=False)
        self.assertEqual(result['newline'], 'unix')
        self.assertEqual(result['max_line_length'], 45)
        self.assertFalse(result['keep_links'])
        self.assertEqual(result['txt_output_encoding'], 'utf-8')


if __name__ == '__main__':
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(MarkdownTests))
    raise SystemExit(not result.wasSuccessful())
