import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('tag_cloud_core', Path(__file__).parents[1] / 'src' / 'core.py')
core = importlib.util.module_from_spec(spec)
spec.loader.exec_module(core)


class CloudTests(unittest.TestCase):
    def test_counts_unique_tags_per_book(self):
        self.assertEqual(core.count_tags({1: ('歷史', '歷史'), 2: ('歷史', '台灣'), 3: ()}),
                         [('歷史', 2), ('台灣', 1)])

    def test_search_escapes_literal_names(self):
        self.assertEqual(core.tag_query(['a"b', r'c\d']), r'tags:"=a\"b" and tags:"=c\\d"')
        self.assertEqual(core.tag_query(['歷史', '台灣'], False), 'tags:"=歷史" or tags:"=台灣"')
        self.assertEqual(core.tag_query([]), '')

    def test_font_bounds_and_equal_counts(self):
        self.assertEqual(core.font_size(1, 1), 12)
        self.assertEqual(core.font_size(10000, 10000), 24)
        self.assertTrue(12 <= core.font_size(12, 10000) <= 24)

    def test_series_and_authors(self):
        self.assertEqual(core.count_tags({1: '系列甲', 2: '系列甲', 3: None}), [('系列甲', 2)])
        self.assertEqual(core.tag_query(['作者甲'], field='authors'), 'authors:"=作者甲"')
        self.assertEqual(core.tag_query(['系列甲'], field='#myseries'), '#myseries:"=系列甲"')


if __name__ == '__main__':
    unittest.main()
