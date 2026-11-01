import importlib.util
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

sys.dont_write_bytecode = True
SOURCE = Path(__file__).resolve().parents[1] / 'src'
spec = importlib.util.spec_from_file_location(
    'calibre_plugins.skip_ascii_text', SOURCE / '__init__.py',
    submodule_search_locations=[str(SOURCE)])
plugin = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = plugin
spec.loader.exec_module(plugin)
from calibre.utils import filenames
from calibre_plugins.skip_ascii_text import config, main, ui


class SkipASCIITextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from qt.core import QApplication
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.original = filenames.ascii_text
        self.module_marker = object()
        state_patch = patch.object(main, '_previous_ascii_text', None)
        state_patch.start()
        self.addCleanup(state_patch.stop)
        self.addCleanup(setattr, filenames, 'ascii_text', self.original)

    def apply(self, enabled):
        main.set_enabled(enabled)

    def test_preserves_text_and_decodes_bytes(self):
        self.apply(True)
        for value in ('書店怪問', '書店怪問'.encode('utf-8')):
            self.assertEqual(filenames.ascii_filename(value), '書店怪問')
        self.assertIsInstance(filenames.ascii_text(b'\xff'), str)

    def test_still_sanitizes_invalid_characters(self):
        self.apply(True)
        self.assertEqual(filenames.ascii_filename('書店:怪問?'), '書店_怪問_')

    def test_repeated_enable_restores_original(self):
        self.apply(True)
        self.apply(True)
        self.apply(False)
        self.apply(False)
        self.assertIs(filenames.ascii_text, self.original)
        self.apply(True)
        self.apply(False)
        self.assertIs(filenames.ascii_text, self.original)

    def test_restores_preexisting_patch_without_reloading_module(self):
        def previous(value):
            return 'previous'
        with patch.object(filenames, 'ascii_text', previous), \
                patch.object(filenames, 'ascii_filename', self.module_marker):
            self.apply(True)
            self.apply(False)
            self.assertIs(filenames.ascii_text, previous)
            self.assertIs(filenames.ascii_filename, self.module_marker)

    def test_disable_leaves_later_patch_untouched(self):
        self.apply(True)
        def later(value):
            return 'later'
        filenames.ascii_text = later
        self.apply(False)
        self.assertIs(filenames.ascii_text, later)

    def test_initially_disabled_does_not_change_function(self):
        self.apply(False)
        self.assertIs(filenames.ascii_text, self.original)

    def test_settings_save_updates_core_and_chinese_status(self):
        settings = {'SKIP_ASCII_TEXT': True}
        action = SimpleNamespace(qaction=Mock())
        action.apply_settings = lambda: ui.SkipASCIITextPlugin.apply_settings(action)
        with patch.object(config, 'prefs', settings), patch.object(ui, 'prefs', settings):
            widget = config.ConfigWidget()
            self.assertTrue(widget.enabled.isChecked())
            self.assertIn('原文字元', widget.enabled.text())
            action.apply_settings()
            self.assertIs(filenames.ascii_text, main.preserve_unicode)
            widget.enabled.setChecked(False)
            plugin.SkipASCIIText.save_settings(SimpleNamespace(actual_plugin_=action), widget)
            self.assertFalse(settings['SKIP_ASCII_TEXT'])
            self.assertIs(filenames.ascii_text, self.original)
            action.qaction.setToolTip.assert_called_with('保留原文字元：已停用')
            widget.deleteLater()

    def test_toolbar_uses_text_icon_and_configuration(self):
        action = SimpleNamespace(qaction=Mock(), configure=Mock())
        ui.SkipASCIITextPlugin.genesis(action)
        action.qaction.triggered.connect.assert_called_once_with(action.configure)

    def test_large_font_dialog_has_no_scroll_area(self):
        from qt.core import QFont, QScrollArea
        original_font = self.app.font()
        font = QFont(original_font)
        font.setPointSize(20)
        self.app.setFont(font)
        try:
            dialog = config.SettingsDialog()
            dialog.show()
            self.app.processEvents()
            self.assertFalse(dialog.findChildren(QScrollArea))
            checkbox = dialog.settings.enabled
            self.assertGreaterEqual(checkbox.width(), checkbox.sizeHint().width())
            self.assertGreaterEqual(dialog.width(), dialog.minimumSizeHint().width())
            dialog.settings.enabled.setChecked(False)
            self.assertEqual(dialog.settings.result.text(), 'Shu Dian Guai Wen')
            dialog.close()
            dialog.deleteLater()
        finally:
            self.app.setFont(original_font)

    def test_dialog_save_and_cancel(self):
        from qt.core import QApplication, QTimer
        action = SimpleNamespace(save_settings=Mock())
        def save():
            dialog = QApplication.activeModalWidget()
            dialog.settings.enabled.setChecked(False)
            dialog.accept()
        QTimer.singleShot(0, save)
        self.assertTrue(plugin.SkipASCIIText.do_user_config(action))
        action.save_settings.assert_called_once()
        action.save_settings.reset_mock()
        QTimer.singleShot(0, lambda: QApplication.activeModalWidget().reject())
        self.assertFalse(plugin.SkipASCIIText.do_user_config(action))
        action.save_settings.assert_not_called()


if __name__ == '__main__':
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(SkipASCIITextTests))
    raise SystemExit(not result.wasSuccessful())
