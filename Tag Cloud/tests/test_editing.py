import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
from calibre.db.legacy import LibraryDatabase
from calibre.ebooks.metadata.book.base import Metadata
from calibre.gui2 import Application

source = Path(__file__).parents[1] / 'src'
spec = importlib.util.spec_from_file_location('calibre_plugins.tag_cloud', source / '__init__.py',
                                            submodule_search_locations=[str(source)])
plugin = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = plugin
spec.loader.exec_module(plugin)
from calibre_plugins.tag_cloud import editing


class EditingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = Application.instance() or Application([])

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path(__file__).parents[2] / 'dist')
        self.db = LibraryDatabase(self.temp.name)
        self.ids = []
        for title, tags in [('甲', ['歷史', '台灣']), ('乙', ['歷史', '其他']), ('丙', ['科幻'])]:
            mi = Metadata(title, ['作者甲'])
            mi.tags = tags
            mi.series, mi.series_index = '系列甲', 3.5
            self.ids.append(self.db.create_book_entry(mi))

    def tearDown(self):
        self.db.close()
        self.temp.cleanup()

    def test_multi_value_merge_and_scope(self):
        api = self.db.new_api
        change = editing.prepare(api, 'tags', '歷史', {self.ids[0]}, '台灣')
        editing.apply(api, change)
        self.assertEqual(api.field_for('tags', self.ids[0]), ('台灣',))
        self.assertIn('歷史', api.field_for('tags', self.ids[1]))
        change = editing.prepare(api, 'tags', '台灣', {self.ids[0]}, remove=True)
        editing.apply(api, change)
        self.assertEqual(api.field_for('tags', self.ids[0]), ())

    def test_author_last_value_and_title_guard(self):
        from calibre.utils.localization import _
        api = self.db.new_api
        editing.apply(api, editing.prepare(api, 'authors', '作者甲', {self.ids[0]}, remove=True))
        self.assertEqual(api.field_for('authors', self.ids[0]), (_('Unknown'),))
        with self.assertRaises(ValueError):
            editing.prepare(api, 'title', '甲', {self.ids[0]}, remove=True)

    def test_series_preserves_index_and_clear_resets_it(self):
        api = self.db.new_api
        editing.apply(api, editing.prepare(api, 'series', '系列甲', {self.ids[0]}, '系列乙'))
        self.assertEqual(api.field_for('series_index', self.ids[0]), 3.5)
        editing.apply(api, editing.prepare(api, 'series', '系列乙', {self.ids[0]}, remove=True))
        self.assertIsNone(api.field_for('series', self.ids[0]))
        self.assertEqual(api.field_for('series_index', self.ids[0]), 1.0)

    def test_identifiers_preserve_other_entries(self):
        api = self.db.new_api
        api.set_field('identifiers', {self.ids[0]: {'isbn': '123', 'asin': 'ABC'}})
        editing.apply(api, editing.prepare(api, 'identifiers', 'isbn:123', {self.ids[0]}, '456'))
        self.assertEqual(api.field_for('identifiers', self.ids[0]), {'isbn': '456', 'asin': 'ABC'})

    def test_readonly_and_concurrent_change(self):
        api = self.db.new_api
        self.assertTrue(editing.readonly_reason(api, 'id'))
        change = editing.prepare(api, 'tags', '歷史', {self.ids[0]}, '新標籤')
        api.set_field('tags', {self.ids[0]: ['使用者剛改的值']})
        with self.assertRaises(ValueError):
            editing.apply(api, change)
        self.assertEqual(api.field_for('tags', self.ids[0]), ('使用者剛改的值',))

    def test_scalar_rating_date_and_comments(self):
        from datetime import datetime, timezone
        api = self.db.new_api
        book_id = self.ids[0]
        api.set_field('rating', {book_id: 10})
        editing.apply(api, editing.prepare(api, 'rating', '5 ★', {book_id}, 7))
        self.assertEqual(api.field_for('rating', book_id), 7)
        editing.apply(api, editing.prepare(api, 'rating', '3.5 ★', {book_id}, remove=True))
        self.assertIsNone(api.field_for('rating', book_id))
        api.set_field('pubdate', {book_id: datetime(2020, 1, 1, tzinfo=timezone.utc)})
        editing.apply(api, editing.prepare(api, 'pubdate', '2020-01-01', {book_id},
                                          datetime(2021, 2, 3, tzinfo=timezone.utc)))
        self.assertEqual(api.field_for('pubdate', book_id).year, 2021)
        api.set_field('comments', {book_id: '<p>完整原文</p>'})
        editing.apply(api, editing.prepare(api, 'comments', '完整原文', {book_id}, '<p>更新原文</p>'))
        self.assertEqual(api.field_for('comments', book_id), '<p>更新原文</p>')

    def test_custom_types_and_series(self):
        for label, kind in [('flag', 'bool'), ('number', 'int'), ('decimal', 'float'), ('sequence', 'series'),
                            ('computed', 'composite')]:
            self.db.create_custom_column(label, label, kind, False)
        self.db.create_custom_column('choice', 'choice', 'enumeration', False, display={'enum_values': ['甲', '乙']})
        self.db.create_custom_column('topics', 'topics', 'text', True)
        self.db.close()
        self.db = LibraryDatabase(self.temp.name)
        api = self.db.new_api
        book_id = self.ids[0]
        self.assertTrue(editing.readonly_reason(api, '#computed'))
        for field, old, term, new in [('#flag', True, '是', False), ('#number', 3, '3', 8),
                                      ('#decimal', 1.5, '1.5', 2.25)]:
            api.set_field(field, {book_id: old})
            editing.apply(api, editing.prepare(api, field, term, {book_id}, new))
            self.assertEqual(api.field_for(field, book_id), new)
        api.set_field('#sequence', {book_id: '甲'})
        api.set_field('#sequence_index', {book_id: 7.25})
        editing.apply(api, editing.prepare(api, '#sequence', '甲', {book_id}, '乙'))
        self.assertEqual(api.field_for('#sequence_index', book_id), 7.25)
        api.set_field('#choice', {book_id: '甲'})
        editing.apply(api, editing.prepare(api, '#choice', '甲', {book_id}, '乙'))
        self.assertEqual(api.field_for('#choice', book_id), '乙')
        with self.assertRaises(ValueError):
            editing.prepare(api, '#choice', '乙', {book_id}, '不允許的值')
        api.set_field('#topics', {book_id: ['歷史', '台灣']})
        editing.apply(api, editing.prepare(api, '#topics', '歷史', {book_id}, '台灣'))
        self.assertEqual(api.field_for('#topics', book_id), ('台灣',))

    def test_failed_write_restores_original(self):
        from unittest.mock import patch
        api = self.db.new_api
        change = editing.prepare(api, 'tags', '歷史', {self.ids[0]}, '新值')
        original = api.set_field
        calls = []
        def fail_after_write(*args, **kwargs):
            result = original(*args, **kwargs)
            calls.append(1)
            if len(calls) == 1:
                raise RuntimeError('模擬部分寫入後失敗')
            return result
        with patch.object(api, 'set_field', side_effect=fail_after_write):
            with self.assertRaisesRegex(RuntimeError, '已還原'):
                editing.apply(api, change)
        self.assertEqual(api.field_for('tags', self.ids[0]), ('歷史', '台灣'))

    def test_case_only_and_invalid_values_do_not_write(self):
        api = self.db.new_api
        book_id = self.ids[0]
        api.set_field('tags', {book_id: ['Old']})
        with self.assertRaises(ValueError):
            editing.prepare(api, 'tags', 'Old', {book_id}, 'OLD')
        api.set_field('rating', {book_id: 8})
        with self.assertRaises(ValueError):
            editing.prepare(api, 'rating', '4 ★', {book_id}, 20)
        self.assertEqual(api.field_for('tags', book_id), ('Old',))

    def test_metadata_changes_survive_database_reopen(self):
        api = self.db.new_api
        editing.apply(api, editing.prepare(api, 'tags', '歷史', {self.ids[0]}, '新歷史'))
        self.db.close()
        self.db = LibraryDatabase(self.temp.name)
        self.assertEqual(self.db.new_api.field_for('tags', self.ids[0]), ('新歷史', '台灣'))
        self.assertEqual(self.db.new_api.field_for('tags', self.ids[1]), ('歷史', '其他'))

    def test_series_write_failure_restores_name_and_index(self):
        from unittest.mock import patch
        api = self.db.new_api
        book_id = self.ids[0]
        change = editing.prepare(api, 'series', '系列甲', {book_id}, remove=True)
        original = api.set_field
        calls = []
        def fail_index(*args, **kwargs):
            result = original(*args, **kwargs)
            calls.append(1)
            if len(calls) == 2:
                raise RuntimeError('模擬系列編號寫入失敗')
            return result
        with patch.object(api, 'set_field', side_effect=fail_index):
            with self.assertRaisesRegex(RuntimeError, '已還原'):
                editing.apply(api, change)
        self.assertEqual(api.field_for('series', book_id), '系列甲')
        self.assertEqual(api.field_for('series_index', book_id), 3.5)


if __name__ == '__main__':
    result = unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(EditingTests))
    raise SystemExit(not result.wasSuccessful())
