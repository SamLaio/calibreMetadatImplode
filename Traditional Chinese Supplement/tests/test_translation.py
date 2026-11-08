import importlib.util
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
from calibre.utils.config import config_dir
if (ROOT / 'dist').resolve() not in Path(config_dir).resolve().parents:
    raise SystemExit('請使用 dist 下的獨立 CALIBRE_CONFIG_DIRECTORY。')
spec = importlib.util.spec_from_file_location(
    'calibre_plugins.traditional_chinese_supplement',
    ROOT / 'Traditional Chinese Supplement/src/__init__.py',
    submodule_search_locations=[str(ROOT / 'Traditional Chinese Supplement/src')])
plugin = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = plugin
spec.loader.exec_module(plugin)
from calibre_plugins.traditional_chinese_supplement import ui
from calibre.gui2 import Application
from qt.core import QApplication, QCheckBox, QDialog, QFont, QFontDatabase


class TranslationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or Application([])
        font_id = QFontDatabase.addApplicationFont('C:/Windows/Fonts/msjh.ttc')
        families = QFontDatabase.applicationFontFamilies(font_id)
        if families:
            cls.app.setFont(QFont(families[0], 12))

    def setUp(self):
        self.db = Mock()
        self.dialogs = []
        self.translator = ui.TranslationFilter()
        self.locale = patch.object(ui, 'get_lang', return_value='zh_TW')
        self.locale.start()

    def tearDown(self):
        self.translator.stop()
        for dialog in self.dialogs:
            dialog.close()
            dialog.deleteLater()
        self.app.processEvents()
        self.locale.stop()

    def dialog(self):
        dialog = ui.Polish(self.db, {})
        self.dialogs.append(dialog)
        for name, (english, chinese) in ui.LABELS.items():
            getattr(dialog, 'opt_' + name).setText(english)
        dialog.help_text['download_external_resources'] = (
            '<h3>Download external resources</h3>' + ui.DOWNLOAD_HELP)
        return dialog

    def test_later_real_dialog_and_help_links(self):
        self.translator.start()
        dialog = self.dialog()
        before = list(dialog.all_actions)
        dialog.opt_subset.setChecked(True)
        dialog.show()
        self.app.processEvents()
        for name, (english, chinese) in ui.LABELS.items():
            checkbox = getattr(dialog, 'opt_' + name)
            self.assertEqual(checkbox.text(), chinese)
            self.assertFalse(checkbox.shortcut().isEmpty())
            dialog.help_link_activated('#' + name)
            for heading in ui.HEADINGS:
                self.assertNotIn('<h3>' + heading + '</h3>', dialog.help_label.text())
        self.assertEqual(list(dialog.all_actions), before)
        self.assertTrue(dialog.opt_subset.isChecked())
        dialog.help_link_activated('#download_external_resources')
        self.assertIn('下載圖片', dialog.help_label.text())
        self.assertNotIn('Download external resources', dialog.help_label.text())
        dialog.resize(1250, 780)
        self.app.processEvents()
        dialog.grab().save(str(ROOT / 'dist/translation-qa/polish-zh_TW.png'))

    def test_existing_window_and_current_help(self):
        dialog = self.dialog()
        dialog.show()
        dialog.help_link_activated('#download_external_resources')
        self.translator.start()
        self.assertEqual(dialog.opt_subset.text(), ui.LABELS['subset'][1])
        self.assertIn('下載圖片', dialog.help_label.text())

    def test_preserves_chinese_and_unknown_text(self):
        dialog = self.dialog()
        dialog.opt_subset.setText('官方已翻好的中文')
        dialog.opt_do_cover.setText('A future changed message')
        dialog.help_text['subset'] = '<h3>官方中文說明</h3>保留原文'
        original = dialog.opt_embed.text()
        ui.translate_polish(dialog)
        ui.translate_polish(dialog)
        self.assertEqual(dialog.opt_subset.text(), '官方已翻好的中文')
        self.assertEqual(dialog.opt_do_cover.text(), 'A future changed message')
        self.assertEqual(dialog.help_text['subset'], '<h3>官方中文說明</h3>保留原文')
        self.assertEqual(dialog.opt_embed.text(), original)

    def test_other_dialog_is_untouched(self):
        self.translator.start()
        dialog = QDialog()
        self.dialogs.append(dialog)
        checkbox = QCheckBox(ui.LABELS['subset'][0], dialog)
        dialog.show()
        self.app.processEvents()
        self.assertEqual(checkbox.text(), ui.LABELS['subset'][0])

    def test_other_language_is_untouched(self):
        with patch.object(ui, 'get_lang', return_value='en'):
            self.translator.start()
        dialog = self.dialog()
        dialog.show()
        self.app.processEvents()
        self.assertEqual(dialog.opt_subset.text(), ui.LABELS['subset'][0])

    def test_real_kfx_settings_preserve_saved_values(self):
        import os
        from calibre.customize.zipplugin import loader
        archive = Path(os.environ['APPDATA']) / 'calibre/plugins/KFX Input.zip'
        if not archive.is_file():
            self.skipTest('需要已安裝的 KFX Input ZIP')
        plugin_class = loader.load(str(archive))
        self.translator.start()
        widget = plugin_class(str(archive)).config_widget()
        self.dialogs.append(widget)
        self.assertTrue(ui.is_kfx_config(widget))
        combo = widget.ShowCompletionPopup
        combo.setCurrentIndex(2)
        data = [combo.itemData(i) for i in range(combo.count())]
        widget.SplitLandscapeComicImages.setChecked(True)
        widget.DesaturateNotebooks.setChecked(True)
        with patch.object(widget, 'save_settings', wraps=widget.save_settings) as save:
            widget.show()
            self.app.processEvents()
            self.assertEqual(combo.currentIndex(), 2)
            self.assertEqual([combo.itemData(i) for i in range(combo.count())], data)
            self.assertEqual([combo.itemText(i) for i in range(combo.count())],
                             ['僅在轉換錯誤時', '一律顯示', '永不顯示'])
            self.assertIn('漫畫', widget.SplitLandscapeComicImages.text())
            self.assertIn('降低色彩', widget.DesaturateNotebooks.text())
            save.assert_not_called()
        for index in range(3):
            combo.setCurrentIndex(index)
            widget.save_settings()
            config = sys.modules[type(widget).__module__].plugin_config
            self.assertEqual(config['ShowCompletionPopup'], index)
            self.assertTrue(config['SplitLandscapeComicImages'])
            self.assertTrue(config['DesaturateNotebooks'])
        widget.grab().save(str(ROOT / 'dist/translation-qa/kfx-input-zh_TW.png'))

    def test_stop_removes_filter(self):
        self.translator.start()
        self.translator.stop()
        dialog = self.dialog()
        dialog.show()
        self.app.processEvents()
        self.assertEqual(dialog.opt_subset.text(), ui.LABELS['subset'][0])


if __name__ == '__main__':
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(TranslationTests))
    raise SystemExit(not result.wasSuccessful())
