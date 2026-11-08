import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    'calibre_plugins.modify_epub', ROOT / 'Modify ePub/src/__init__.py',
    submodule_search_locations=[str(ROOT / 'Modify ePub/src')])
plugin = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = plugin
spec.loader.exec_module(plugin)
from calibre_plugins.modify_epub.covers import CoverUpdater
from calibre_plugins.modify_epub.modify import BookModifier
from calibre.ebooks.oeb.transforms.cover import CoverManager
import calibre.ebooks.oeb.polish as polish


class CoverTests(unittest.TestCase):
    def test_remove_cover_constructor_and_call(self):
        container = SimpleNamespace(is_drm_encrypted=lambda: False)
        job = SimpleNamespace(log=Mock())
        with patch.object(CoverUpdater, 'remove_existing_cover') as remove:
            self.assertTrue(BookModifier._remove_cover(job, container))
            remove.assert_called_once()

    def test_titlepage_old_and_new_metadata_api(self):
        for modern in (False, True):
            for svg in (False, True):
                with self.subTest(modern=modern, svg=svg), tempfile.TemporaryDirectory(dir=ROOT / 'dist') as folder:
                    container = SimpleNamespace(root=folder)
                    opts = SimpleNamespace(no_svg_cover=not svg, preserve_cover_aspect_ratio=True)
                    updater = CoverUpdater(Mock(), container, None, '中文 & 100% 封面', opts)
                    updater.text_folder = ''
                    template = '<html lang="__lang__"><head><title>__title__</title></head><body><img src="%s" /></body></html>'
                    def fill(text, title, language):
                        return text.replace('__title__', title.replace('&', '&amp;').replace('%', '%%')).replace('__lang__', language)
                    if modern:
                        context = patch.object(polish, 'get_book_language_tag', return_value='zh-TW', create=True)
                        metadata = patch.object(CoverManager, 'fill_metadata', side_effect=fill, create=True)
                    else:
                        context = patch.dict(sys.modules, {'calibre.ebooks.oeb.polish': None})
                        metadata = patch.object(CoverManager, 'fill_metadata', create=True)
                        template = template.replace('__title__', 'Cover').replace('__lang__', 'en')
                    with context, metadata as method, patch.object(CoverManager, 'SVG_TEMPLATE', template), patch.object(CoverManager, 'NONSVG_TEMPLATE', template):
                        name = updater._create_titlepage('images/cover.jpg', 600, 800)
                    text = (Path(folder) / name).read_text(encoding='utf-8')
                    self.assertNotIn('__title__', text)
                    self.assertNotIn('__lang__', text)
                    self.assertIn('images/cover.jpg', text)
                    if modern:
                        method.assert_called_once_with(template, updater.title, 'zh-TW')
                        self.assertIn('中文 &amp; 100% 封面', text)
                    else:
                        method.assert_not_called()


if __name__ == '__main__':
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(CoverTests))
    raise SystemExit(not result.wasSuccessful())
