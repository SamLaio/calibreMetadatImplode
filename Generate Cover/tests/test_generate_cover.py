import copy
import gettext
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch
from zipfile import ZipFile

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'Generate Cover' / 'src'
from calibre.utils.config import config_dir
if (ROOT / 'dist').resolve() not in Path(config_dir).resolve().parents:
    raise SystemExit('請先將 CALIBRE_CONFIG_DIRECTORY 設為本專案 dist/qa-config。')

spec = importlib.util.spec_from_file_location(
    'calibre_plugins.generate_cover', SOURCE / '__init__.py',
    submodule_search_locations=[str(SOURCE)])
plugin = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = plugin
spec.loader.exec_module(plugin)
from calibre_plugins.generate_cover import action, config as cfg, dialogs, draw
from calibre.ebooks.metadata.book.base import Metadata
from calibre.gui2 import Application
from calibre.utils.magick.draw import create_canvas
from qt.core import QApplication, QImage, Qt, QFont, QFontDatabase


class GenerateCoverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or Application([])
        font_file = Path('C:/Windows/Fonts/msjh.ttc')
        if font_file.exists():
            font_id = QFontDatabase.addApplicationFont(str(font_file))
            families = QFontDatabase.applicationFontFamilies(font_id)
            if families:
                cls.app.setFont(QFont(families[0], 12))

    def setUp(self):
        self.options = copy.deepcopy(cfg.DEFAULT_CURRENT)
        self.book = Metadata('書店怪問', ['珍．坎貝爾'])
        self.book.id = 12
        self.book.series = '書店系列'
        self.book.series_index = 2
        self.options[cfg.KEY_SERIES_TEXT] = '{series} 第 {series_index} 集'

    def test_font_families_match_qt(self):
        model = dialogs.FontFamilyModel()
        self.assertTrue(model.families)
        self.assertEqual(list(model.families), list(QFontDatabase.families()))
        self.assertEqual(model.rowCount(), len(model.families))
        self.assertEqual(model.index_of(model.families[0]), 0)

    def test_actual_chinese_cover(self):
        self.options[cfg.KEY_IMAGE_FILE] = cfg.TOKEN_CURRENT_COVER
        for field in self.options[cfg.KEY_FIELD_ORDER]:
            if field['name'] == 'Image':
                field['display'] = False
        data = draw.generate_cover_for_book(self.book, self.options)
        image = QImage.fromData(data)
        self.assertFalse(image.isNull())
        self.assertEqual((image.width(), image.height()), (590, 750))
        self.assertTrue(any(image.pixelColor(x, y).lightness() < 100
                            for x in range(0, 590, 5) for y in range(0, 250, 5)))
        (ROOT / 'dist' / 'generate-cover-example.jpg').write_bytes(data)

    def test_autofit_handles_fractional_margins_and_tiny_font(self):
        line = draw.TextLine('極長文字' * 1000, None, 8)
        line.apply_element_options(cfg.default_field('Title', True))
        original_set = line.font.setPixelSize
        def positive_size(size):
            self.assertGreater(size, 0)
            original_set(size)
        with patch.object(line.font, 'setPixelSize', side_effect=positive_size):
            draw.draw_sized_text(create_canvas(100, 200), draw.create_colored_text_wand(line),
                                 line, 0, 5.5, 4.5, True)
        self.assertLess(len(line.text), 100)

    def test_rotated_text_and_backdrop_render(self):
        for angle in (90, 180, 270):
            options = copy.deepcopy(self.options)
            options[cfg.KEY_IMAGE_FILE] = cfg.TOKEN_CURRENT_COVER
            options[cfg.KEY_FIELD_ORDER][0][cfg.KEY_FIELD_ROTATION] = angle
            options[cfg.KEY_FIELD_ORDER][0][cfg.KEY_FIELD_BACKDROP] = True
            data = draw.generate_cover_for_book(self.book, options)
            self.assertFalse(QImage.fromData(data).isNull())

    def test_small_cover_with_maximum_border_still_renders(self):
        self.options[cfg.KEY_SIZE] = (100, 100)
        self.options[cfg.KEY_BORDERS]['coverBorder'] = 99
        self.options[cfg.KEY_IMAGE_FILE] = cfg.TOKEN_CURRENT_COVER
        image = QImage.fromData(draw.generate_cover_for_book(self.book, self.options))
        self.assertEqual((image.width(), image.height()), (100, 100))

    def test_real_image_and_background_modes(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'dist') as folder:
            sample = QImage(64, 64, QImage.Format_RGB32)
            sample.fill(Qt.blue)
            sample.save(str(Path(folder) / 'sample.png'))
            self.options[cfg.KEY_IMAGE_FILE] = 'sample.png'
            self.options[cfg.KEY_SIZE] = (150, 200)
            self.options[cfg.KEY_BORDERS]['imageBorder'] = 99
            for field in self.options[cfg.KEY_FIELD_ORDER]:
                field['display'] = field['name'] == 'Image'
            with patch.object(cfg, 'get_images_dir', return_value=folder):
                for background in (False, True):
                    self.options[cfg.KEY_BACKGROUND_IMAGE] = background
                    image = QImage.fromData(draw.generate_cover_for_book(self.book, self.options))
                    self.assertFalse(image.isNull())
                    self.assertEqual((image.width(), image.height()), (150, 200))

    def test_batch_cancel_does_not_write_cover(self):
        job = SimpleNamespace(i=0, total_count=1, wasCanceled=lambda: True, do_close=Mock())
        with patch.object(dialogs, 'generate_cover_for_book') as generate:
            dialogs.GenerateCoverProgressDialog.do_generate_cover(job)
        generate.assert_not_called()
        job.do_close.assert_called_once()

    def test_batch_error_does_not_replace_cover_and_continues(self):
        job = SimpleNamespace(i=0, total_count=1, wasCanceled=lambda: False,
                              books=[self.book], options=self.options, db=Mock(),
                              errors=[], setLabelText=Mock(), setValue=Mock(), do_generate_cover=Mock())
        with patch.object(dialogs, 'generate_cover_for_book', side_effect=ValueError('bad image')), \
                patch.object(dialogs.QTimer, 'singleShot') as timer:
            dialogs.GenerateCoverProgressDialog.do_generate_cover(job)
        job.db.set_cover.assert_not_called()
        self.assertEqual(job.i, 1)
        self.assertIn('bad image', job.errors[0])
        timer.assert_called_once()

    def test_image_destination_rejects_paths_and_links(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'dist') as folder:
            self.assertEqual(Path(dialogs.image_destination(folder, '封面.png')), Path(folder) / '封面.png')
            for name in ('../outside.png', '..\\outside.png', '/absolute.png', 'C:cover.png', '.', ''):
                with self.assertRaises(ValueError):
                    dialogs.image_destination(folder, name)
            with patch.object(dialogs.os.path, 'realpath', side_effect=[folder, str(Path(folder).parent / 'outside.png')]):
                with self.assertRaises(ValueError):
                    dialogs.image_destination(folder, 'link.png')

    def test_different_setting_lengths_compare_without_crashing(self):
        compare = lambda left, right: dialogs.CoverOptionsDialog.compare_items(
            SimpleNamespace(compare_items=compare), left, right)
        self.assertFalse(compare([1, 2], [1]))
        self.assertFalse(compare([1], [1, 2]))
        self.assertFalse(compare({'a': 1}, {'a': 1, 'b': 2}))
        self.assertTrue(compare((1, 2), [1, 2]))

    def test_translated_field_label_keeps_internal_key(self):
        with patch.object(dialogs, '_', side_effect=lambda value: '書名' if value == 'Title' else value, create=True):
            widget = dialogs.FieldOrderListWidget(None)
            fields = [cfg.default_field('Title', True)]
            widget.populate(fields)
            item = widget.item(0)
            self.assertEqual(item.text(), '書名')
            item.setCheckState(Qt.Unchecked)
            self.assertFalse(fields[0]['display'])
            self.assertEqual(fields[0]['name'], 'Title')
            widget.deleteLater()

    def test_old_profile_migrates_without_losing_custom_text(self):
        options = copy.deepcopy(self.options)
        options[cfg.KEY_FIELD_ORDER] = [{'name': 'Title', 'display': True},
                                         {'name': 'Custom Text', 'display': True}]
        options[cfg.KEY_CUSTOM_TEXT] = '自訂內容'
        options[cfg.KEY_IMAGE_FILE] = cfg.TOKEN_DEFAULT_COVER
        cfg.migrate_config_setting(2.22, 'old', options)
        self.assertEqual(options[cfg.KEY_CUSTOM_TEXT], '自訂內容')
        self.assertIn('Custom Text 3', [field['name'] for field in options[cfg.KEY_FIELD_ORDER]])
        self.assertIsInstance(options[cfg.KEY_FIELD_ORDER][0][cfg.KEY_FIELD_TEXT_PADDING], dict)

    def test_import_rejects_escaping_image_before_prompt_or_write(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'dist') as folder:
            archive = Path(folder) / 'unsafe.zip'
            settings = copy.deepcopy(self.options)
            settings[cfg.KEY_IMAGE_FILE] = '../outside.png'
            with ZipFile(archive, 'w') as z:
                z.writestr('gc_setting.json', json.dumps({cfg.STORE_SAVED_SETTINGS: {'unsafe': settings},
                              cfg.STORE_SCHEMA_VERSION: cfg.DEFAULT_SCHEMA_VERSION}))
            tab = SimpleNamespace(check_for_setting_save=Mock(), pick_archive_names_to_import=lambda: [str(archive)],
                                  parent_dialog=SimpleNamespace(images_dir=folder), get_new_setting_name=Mock())
            with patch.object(dialogs, 'error_dialog') as error:
                dialogs.SavedSettingsTab.import_setting(tab)
            error.assert_called_once()
            tab.get_new_setting_name.assert_not_called()
            self.assertFalse((Path(folder) / 'gc_setting.json').exists())

    def test_export_preserves_existing_json_file(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'dist') as folder:
            sentinel = Path(folder) / 'gc_setting.json'
            sentinel.write_text('keep me', encoding='utf-8')
            archive = Path(folder) / 'profile.zip'
            settings = copy.deepcopy(self.options)
            settings[cfg.KEY_IMAGE_FILE] = cfg.TOKEN_DEFAULT_COVER
            tab = SimpleNamespace(check_for_setting_save=Mock(),
                                  saved_setting_list=SimpleNamespace(selected_setting=lambda: settings),
                                  pick_archive_name_to_export=lambda: str(archive),
                                  parent_dialog=SimpleNamespace(images_dir=folder))
            with patch.object(dialogs, 'info_dialog'):
                dialogs.SavedSettingsTab.export_setting(tab)
            self.assertEqual(sentinel.read_text(encoding='utf-8'), 'keep me')
            with ZipFile(archive) as z:
                profile = json.loads(z.read('gc_setting.json'))
            self.assertEqual(profile[cfg.STORE_SCHEMA_VERSION], cfg.DEFAULT_SCHEMA_VERSION)
            self.assertIn(cfg.KEY_DEFAULT, profile[cfg.STORE_SAVED_SETTINGS])

    def test_failed_cover_write_does_not_mark_book_as_updated(self):
        database = Mock()
        database.set_cover.side_effect = OSError('write failed')
        api = SimpleNamespace(gui=SimpleNamespace(current_db=database))
        with patch.object(cfg, 'plugin_prefs', {cfg.STORE_CURRENT: self.options}), \
                patch.object(action, 'generate_cover_for_book', return_value=b'image'), \
                patch.object(action, 'update_custom_columns_if_required') as update:
            with self.assertRaises(OSError):
                action.GenerateCoverAction.generate_cover_for_book(api, self.book)
        update.assert_not_called()

    def test_output_path_is_not_used_as_source_cover(self):
        api = SimpleNamespace(gui=SimpleNamespace(current_db=Mock()))
        with patch.object(cfg, 'plugin_prefs', {cfg.STORE_CURRENT: self.options}), \
                patch.object(action, 'generate_cover_for_book', return_value=b'image'), \
                patch.object(action, 'update_custom_columns_if_required'), \
                patch('calibre.utils.magick.draw.save_cover_data_to') as save:
            action.GenerateCoverAction.generate_cover_for_book(api, self.book, path_to_cover='output.jpg')
        self.assertNotEqual(getattr(self.book, '_path_to_cover', None), 'output.jpg')
        save.assert_called_once_with(b'image', 'output.jpg')

    def test_full_dialog_opens_with_scrollable_tabs(self):
        from calibre_plugins.generate_cover import common_icons
        from qt.core import QIcon, QScrollArea, QWidget
        preferences = {
            cfg.STORE_CURRENT: copy.deepcopy(self.options),
            cfg.STORE_SAVED_SETTINGS: {cfg.KEY_DEFAULT: copy.deepcopy(self.options)},
            cfg.STORE_FILES: list(cfg.TOKEN_COVERS),
            cfg.STORE_OTHER_OPTIONS: copy.deepcopy(cfg.DEFAULT_OTHER_OPTIONS),
        }
        for setting in (preferences[cfg.STORE_CURRENT], preferences[cfg.STORE_SAVED_SETTINGS][cfg.KEY_DEFAULT]):
            setting[cfg.KEY_IMAGE_FILE] = cfg.TOKEN_DEFAULT_COVER
        def icon(name, *args, **kwargs):
            path = SOURCE / name
            return QIcon(str(path)) if path.exists() else QIcon.ic(name)
        gui = QWidget()
        gui.current_db = SimpleNamespace(new_api=Mock())
        api = SimpleNamespace(gui=gui, interface_action_base_plugin=Mock())
        resources = {str(p.relative_to(SOURCE)).replace('\\', '/'): p.read_bytes()
                     for p in (SOURCE / 'images').glob('*') if p.is_file()}
        with tempfile.TemporaryDirectory(dir=ROOT / 'dist') as folder, \
                patch.object(cfg, 'plugin_prefs', preferences), \
                patch.object(common_icons, 'plugin_icon_resources', resources), \
                patch.object(common_icons, 'get_icons', side_effect=icon, create=True):
            dialog = dialogs.CoverOptionsDialog(api, folder, self.book, False)
            self.assertEqual(len(dialog.findChildren(QScrollArea)), 3)
            self.assertEqual(dialog.minimumHeight(), 500)
            background = dialog.contents_tab.background_image_checkbox
            fit = dialog.dimensions_tab.resize_image_to_fit_checkbox
            match = dialog.dimensions_tab.resize_to_image_checkbox
            fit.setChecked(True)
            self.assertTrue(background.isEnabled())
            background.click()
            self.assertTrue(background.isChecked())
            self.assertFalse(fit.isChecked())
            self.assertTrue(dialog.current[cfg.KEY_BACKGROUND_IMAGE])
            match.setChecked(True)
            self.assertFalse(dialog.dimensions_tab.width_spin.isEnabled())
            background.click()
            self.assertFalse(match.isChecked())
            self.assertTrue(dialog.dimensions_tab.width_spin.isEnabled())
            self.assertTrue(dialog.dimensions_tab.height_spin.isEnabled())
            background.click()
            fit.click()
            self.assertFalse(background.isChecked())
            self.assertTrue(fit.isChecked())
            dialog.terminate()
            dialog.close()
            dialog.deleteLater()

    def test_packaged_translation_is_complete_and_not_mixed(self):
        expected = {json.loads(line[len('msgid '):]) for line in
                    (SOURCE / 'translations' / 'zh_TW.po').read_text(encoding='utf-8').splitlines()
                    if line.startswith('msgid ')}
        with ZipFile(ROOT / 'dist' / 'Generate Cover-zh_TW-release.zip') as archive:
            translation = gettext.GNUTranslations(io.BytesIO(archive.read('translations/zh_TW.mo')))
        self.assertEqual(set(translation._catalog), expected)
        self.assertEqual(translation.gettext('Generate Cover'), '產生封面')
        self.assertEqual(translation.gettext('Custom Text 3'), '自訂文字 3')


if __name__ == '__main__':
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(GenerateCoverTests))
    raise SystemExit(not result.wasSuccessful())
