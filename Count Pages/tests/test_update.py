import ast
import gettext
import importlib.util
import io
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1] / 'src'
spec = importlib.util.spec_from_file_location(
    'calibre_plugins.count_pages', SOURCE / '__init__.py',
    submodule_search_locations=[str(SOURCE)])
plugin = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = plugin
spec.loader.exec_module(plugin)

from calibre_plugins.count_pages.download import DownloadPagesWorker
from calibre_plugins.count_pages.nltk_lite.textanalyzer import TextAnalyzer


class UpdateTests(unittest.TestCase):
    def test_goodreads_uses_xml_url_and_parses_page_count(self):
        html = b'<html><script id="__NEXT_DATA__">{"numPages":320,"title":"Test"}</script></html>'
        with patch('calibre_plugins.count_pages.download.browser') as browser:
            browser.return_value.open_novisit.return_value = io.BytesIO(html)
            worker = DownloadPagesWorker([('goodreads', '123')])
            browser.return_value.open_novisit.assert_called_once_with(
                'https://www.goodreads.com/book/show/123.xml', timeout=20)
        self.assertEqual(worker.page_count, 320)
        self.assertEqual(worker.source_name, 'goodreads')

    def test_missing_goodreads_count_tries_next_source(self):
        responses = [b'<html><body>No page count</body></html>',
                     b'<html><span itemprop="numberOfPages">42</span></html>']
        with patch('calibre_plugins.count_pages.download.browser') as browser:
            browser.return_value.open_novisit.side_effect = [
                io.BytesIO(html) for html in responses]
            worker = DownloadPagesWorker([('goodreads', '123'), ('cbdb.cz', '456')])
        self.assertEqual(worker.page_count, 42)
        self.assertEqual(worker.source_name, 'cbdb.cz')

    def test_english_model_loads_and_splits_sentences(self):
        analyzer = TextAnalyzer((SOURCE / 'nltk_lite/english.pickle').read_bytes())
        self.assertEqual(analyzer.getSentences('Hello world. This is a test.'),
                         ['Hello world.', 'This is a test.'])

    def test_traditional_chinese_covers_all_ui_strings(self):
        messages = set()
        for path in SOURCE.rglob('*.py'):
            for node in ast.walk(ast.parse(path.read_bytes())):
                if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                        and node.func.id == '_' and node.args
                        and isinstance(node.args[0], ast.Constant)
                        and isinstance(node.args[0].value, str)):
                    messages.add(node.args[0].value)
        for lang in ['zh_TW', 'zh_Hant', 'zh_Hant_TW']:
            with self.subTest(lang=lang):
                with (SOURCE / 'translations' / (lang + '.mo')).open('rb') as stream:
                    translation = gettext.GNUTranslations(stream)
                self.assertEqual(sorted(s for s in messages
                                        if not translation._catalog.get(s)), [])


if __name__ == '__main__':
    result = unittest.TextTestRunner().run(
        unittest.defaultTestLoader.loadTestsFromTestCase(UpdateTests))
    raise SystemExit(not result.wasSuccessful())
