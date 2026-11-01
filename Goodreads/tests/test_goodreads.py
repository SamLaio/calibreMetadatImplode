import importlib.util
import io
import json
import sys
import unittest
from pathlib import Path
from queue import Queue
from unittest.mock import Mock, patch

SOURCE = Path(__file__).resolve().parents[1] / 'src'
spec = importlib.util.spec_from_file_location('calibre_plugins.goodreads', SOURCE / '__init__.py', submodule_search_locations=[str(SOURCE)])
plugin = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = plugin
spec.loader.exec_module(plugin)
from calibre_plugins.goodreads.worker import Worker, parse_html


class GoodreadsTests(unittest.TestCase):
    def setUp(self):
        self.plugin = plugin.Goodreads.__new__(plugin.Goodreads)
        self.worker = Worker('https://www.goodreads.com/book/show/123.xml', Queue(), Mock(), Mock(), 0, self.plugin)

    def test_match_requires_title_and_author_words(self):
        row = {'bookId': '1', 'bookTitleBare': 'Dark Matter', 'author': {'name': 'Stephen Other'}}
        self.assertFalse(self.plugin._matches(['Dark', 'Tower'], ['Stephen', 'King'], row))
        row.update(bookTitleBare='The Dark Tower: A Novel', author={'name': 'Stephen King'})
        self.assertTrue(self.plugin._matches(['Dark', 'Tower'], ['Stephen', 'King'], row))
        self.assertFalse(self.plugin._matches(['Art'], [], row))

    def test_identifier_verified_against_details(self):
        self.worker.expected_identifiers = {'isbn': '9780385340588'}
        self.assertFalse(self.worker.matches_identifiers({'details': {'isbn13': '9780061240881'}}))
        self.assertTrue(self.worker.matches_identifiers({'details': {'isbn13': '9780385340588'}}))
        self.worker.expected_identifiers = {'asin': 'B012345678'}
        self.assertFalse(self.worker.matches_identifiers({'details': {}}))
        self.assertTrue(self.worker.matches_identifiers({'details': {'asin': 'B012345678'}}))

    def test_isbn10_fallback(self):
        self.assertEqual(self.worker.parse_isbn({'details': {'isbn13': None, 'isbn': '123456789X'}}), '123456789X')

    def test_missing_work_uses_edition_date(self):
        book = {'details': {'publicationTime': 1000}}
        self.assertEqual(self.worker.parse_publish_date(book, None, True).year, 1970)
        self.assertEqual(self.worker.parse_publish_date(book, {'details': None}, True).year, 1970)

    def test_cover_without_length_and_small_placeholder(self):
        response = self.worker.browser.open_novisit.return_value
        response.info.return_value = {}
        self.assertEqual(self.worker.parse_cover({'imageUrl': 'https://example.org/cover.jpg'}), 'https://example.org/cover.jpg')
        response.info.return_value = {'Content-Length': '100'}
        self.assertIsNone(self.worker.parse_cover({'imageUrl': 'https://example.org/cover.jpg'}))

    def test_json_follows_book_references(self):
        book = {'legacyId': 123, 'title': 'Wanted', 'work': {'__ref': 'Work:w'}, 'bookSeries': [{'series': {'__ref': 'Series:s'}, 'userPosition': '2'}]}
        state = {'Book:wanted': book, 'Book:other': {'legacyId': 456, 'title': 'Wrong'}, 'Series:other': {'id': 'other', 'title': 'Wrong'}, 'Series:s': {'id': 's', 'title': 'Right'}, 'Work:w': {'stats': {}}, 'Work:other': {'stats': {'averageRating': 1}}}
        data = {'props': {'pageProps': {'apolloState': state}}}
        root = parse_html('<html><script id="__NEXT_DATA__">' + json.dumps(data) + '</script></html>')
        parsed = self.worker.parse_book_json(root)
        self.assertEqual(parsed[0], book)
        self.assertEqual(self.worker.parse_series(parsed[0], parsed[1]), ('Right', 2.0))
        self.assertEqual(parsed[3], state['Work:w'])

    def test_retry_is_bounded_and_delayed(self):
        self.worker.get_details = Mock(return_value=True)
        with patch('calibre_plugins.goodreads.worker.time.sleep') as sleep:
            self.worker.run()
        self.assertEqual(self.worker.get_details.call_count, 3)
        self.assertEqual(sleep.call_count, 2)

    def test_identify_fallback_after_identifier_mismatch(self):
        self.plugin.get_goodreads_id_from_identifiers = Mock(return_value='123')
        self.plugin._browser = Mock()
        self.plugin._search_title_author = Mock(return_value=[])
        abort = Mock()
        abort.is_set.return_value = False
        worker = Mock(result_found=False)
        worker.is_alive.return_value = False
        with patch('calibre_plugins.goodreads.worker.Worker', return_value=worker):
            self.plugin.identify(Mock(), Queue(), abort, title='Book', authors=['Author'], identifiers={'isbn': '9780385340588'}, timeout=7)
        self.plugin._search_title_author.assert_called_once()


if __name__ == '__main__':
    result = unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(GoodreadsTests))
    raise SystemExit(not result.wasSuccessful())
