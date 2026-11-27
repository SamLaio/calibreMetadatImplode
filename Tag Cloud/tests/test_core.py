import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('tag_cloud_core', Path(__file__).parents[1] / 'src' / 'core.py')
core = importlib.util.module_from_spec(spec)
spec.loader.exec_module(core)


class CloudTests(unittest.TestCase):
    def test_scalar_field_values(self):
        from datetime import datetime
        self.assertEqual(core.field_terms(False, 'bool'), ['否'])
        self.assertEqual(core.field_terms(0, 'int'), ['0'])
        self.assertEqual(core.field_terms(datetime(2026, 11, 27), 'datetime'), ['2026-11-27'])
        self.assertEqual(core.field_terms(10, 'rating'), ['5 ★'])
        self.assertEqual(core.field_terms({'isbn': '123'}, 'text'), ['isbn:123'])
        self.assertEqual(core.indexed_terms({1: True, 2: False, 3: True}, 'bool')[1],
                         {'是': {1, 3}, '否': {2}})

    def test_counts_unique_tags_per_book(self):
        self.assertEqual(core.count_tags({1: ('歷史', '歷史'), 2: ('歷史', '台灣'), 3: ()}),
                         [('歷史', 2), ('台灣', 1)])

    def test_search_escapes_literal_names(self):
        self.assertEqual(core.tag_query(['a"b', r'c\d']), r'tags:"=a\"b" and tags:"=c\\d"')
        self.assertEqual(core.tag_query(['歷史', '台灣'], False), 'tags:"=歷史" or tags:"=台灣"')
        self.assertEqual(core.tag_query([]), '')

    def test_font_bounds_and_equal_counts(self):
        self.assertEqual(core.font_size(1, 1, 1), 20)
        self.assertEqual(core.font_size(10000, 10000, 100), 36)
        self.assertEqual(core.font_size(100, 10000, 100), 12)
        sizes = [core.font_size(n, 1000, 500) for n in (500, 600, 800, 1000)]
        self.assertEqual(sizes, sorted(set(sizes)))
        self.assertGreaterEqual(sizes[-1] - sizes[0], 24)

    def test_series_and_authors(self):
        self.assertEqual(core.count_tags({1: '系列甲', 2: '系列甲', 3: None}), [('系列甲', 2)])
        self.assertEqual(core.tag_query(['作者甲'], field='authors'), 'authors:"=作者甲"')
        self.assertEqual(core.tag_query(['系列甲'], field='#myseries'), '#myseries:"=系列甲"')


if __name__ == '__main__':
    unittest.main()
