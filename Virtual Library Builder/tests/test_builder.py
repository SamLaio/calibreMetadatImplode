import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch, Mock

sys.dont_write_bytecode = True
from calibre.gui2 import Application
from calibre.db.legacy import LibraryDatabase
from calibre.ebooks.metadata.book.base import Metadata
from qt.core import QMainWindow, Qt

source = Path(__file__).parents[1] / 'src'
spec = importlib.util.spec_from_file_location('calibre_plugins.virtual_library_builder', source / '__init__.py', submodule_search_locations=[str(source)])
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
from calibre_plugins.virtual_library_builder import core, ui


class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = Application([])
        cls.app.setQuitOnLastWindowClosed(False)

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(dir=Path(__file__).parents[2] / 'dist')
        self.db = LibraryDatabase(self.temporary.name)
        for title, tags, authors in [('甲', ['科幻', '歷史'], ['作者甲']), ('乙', ['科幻'], ['作者乙']), ('丙', ['歷史'], ['作者甲']), ('丁', ['a"b', 'a\\b', '=x'], ['作者乙'])]:
            mi = Metadata(title, authors)
            mi.tags = tags
            self.db.create_book_entry(mi)
        self.gui = QMainWindow()
        self.gui.current_db = self.db
        self.gui.library_view = SimpleNamespace(model=lambda: SimpleNamespace(refresh=Mock()))
        self.gui.virtual_libraries_changed = Mock()
        self.gui.apply_virtual_library = Mock()
        self.gui.rebuild_vl_tabs = Mock()
        def remove_vl(name, reapply=True):
            saved = dict(self.db.new_api.pref('virtual_libraries', {}))
            saved.pop(name, None)
            self.db.new_api.set_pref('virtual_libraries', saved)
        self.gui._remove_vl = Mock(side_effect=remove_vl)
        self.dialog = ui.BuilderDialog(self.gui)

    def tearDown(self):
        self.dialog.close()
        self.gui.close()
        self.db.close()
        self.temporary.cleanup()

    def test_conditions_and_escaping(self):
        for text, expected in [('科幻', 2), ('a"b', 1), ('a\\b', 1), ('=x', 1)]:
            self.assertEqual(len(self.db.new_api.search(core.condition('tags', 'text', 'eq', text))), expected)
        self.assertEqual(len(self.db.new_api.search(core.condition('tags', 'text', 'contains', '幻'))), 2)
        both = core.expression([core.condition('tags', 'text', 'eq', x) for x in ['科幻', '歷史']])
        self.assertEqual(len(self.db.new_api.search(both)), 1)
        self.assertEqual(len(self.db.new_api.search(both.replace(' and ', ' or '))), 3)

    def test_typed_validation(self):
        for datatype, value in [('int', '1.5'), ('float', 'nan'), ('datetime', '2026-02-31'), ('rating', '6'), ('bool', 'maybe')]:
            with self.assertRaises(ValueError):
                core.condition('x', datatype, 'eq', value)
        self.assertIn('formats', core.fields(self.db))
        self.assertEqual(len(self.db.new_api.search(core.condition('rating', 'rating', 'gt', '3'))), 0)
        self.assertEqual(core.condition('rating', 'rating', 'gt', '3'), 'rating:>3')
        self.assertEqual(core.condition('pubdate', 'datetime', 'lt', '2026-01-01'), 'pubdate:<2026-01-01')
        self.assertEqual(core.condition('#read', 'bool', 'eq', '否'), '#read:false')
        with self.assertRaises(ValueError):
            core.expression([])

    def test_batch_counts_conflicts_and_persistence(self):
        self.assertIn(('科幻', 2), core.batch_values(self.db, 'tags'))
        entries = [('書架', 'tags:"=科幻"')]
        rows = core.plan(self.db, entries)
        core.save(self.db, rows, {})
        expected = dict(self.db.new_api.pref('virtual_libraries', {}))
        self.assertEqual(core.plan(self.db, entries)[0][3], '跳過')
        self.assertEqual(core.plan(self.db, entries, 'rename')[0][0], '書架 (2)')
        self.assertEqual(core.plan(self.db, entries, 'update')[0][3], '更新')
        with self.assertRaises(ValueError):
            core.save(self.db, rows, {})
        self.db.close()
        self.db = LibraryDatabase(self.temporary.name)
        self.assertEqual(self.db.new_api.pref('virtual_libraries', {}), expected)

    def test_invalid_names(self):
        for name in ['', '*x', 'x' * 41]:
            with self.assertRaises(ValueError):
                core.plan(self.db, [(name, 'tags:true')])
        with self.assertRaises(ValueError):
            core.plan(self.db, [('x', 'tags:true'), ('x', 'tags:false')])

    def set_single(self):
        d = self.dialog
        d.name.setText('科幻書架')
        d.conditions.cellWidget(0, 0).setCurrentIndex(d.conditions.cellWidget(0, 0).findData('tags'))
        d.conditions.cellWidget(0, 2).setText('科幻')
        d.preview()
        self.assertTrue(d.create.isEnabled())
        self.assertEqual(d.rows[0][2], 2)

    def test_preview_cancel_and_create(self):
        self.set_single()
        self.dialog.reject()
        self.assertEqual(self.db.new_api.pref('virtual_libraries', {}), {})
        self.dialog.activate.setChecked(True)
        with patch.object(ui, 'question_dialog', return_value=True), patch.object(ui, 'info_dialog'):
            self.dialog.create_libraries()
        self.assertIn('科幻書架', self.db.new_api.pref('virtual_libraries', {}))
        self.gui.apply_virtual_library.assert_called_once_with('科幻書架')

    def test_stale_inputs_and_library(self):
        self.set_single()
        self.dialog.name.setText('changed')
        with patch.object(ui, 'question_dialog', return_value=True), patch.object(ui, 'info_dialog'):
            self.dialog.create_libraries()
        self.assertIn('changed', self.db.new_api.pref('virtual_libraries', {}))
        self.gui.current_db = None
        with self.assertRaises(ValueError):
            self.dialog.inputs()

    def test_batch_ui_filter_and_preview(self):
        d = self.dialog
        d.tabs.setCurrentIndex(1)
        d.filter.setText('科幻')
        d.check_values(True)
        d.preview()
        self.assertEqual(len(d.rows), 1)
        self.assertEqual(d.rows[0][2], 2)
        self.assertIn('科幻', d.rows[0][0])
        self.assertEqual(self.db.new_api.pref('virtual_libraries', {}), {})
        d.check_values(False)
        self.assertFalse(any(d.values.item(r, 0).checkState() == Qt.CheckState.Checked for r in range(d.values.rowCount())))

    def load_existing(self, name, search):
        self.db.new_api.set_pref('virtual_libraries', {name: search, '保留': 'tags:true'})
        self.dialog.refresh_libraries()
        for row in range(self.dialog.libraries.count()):
            if self.dialog.libraries.item(row).data(Qt.ItemDataRole.UserRole) == name:
                self.dialog.libraries.setCurrentRow(row)
                return

    def test_edit_existing_simple(self):
        self.load_existing('既有書庫', 'tags:"=科幻"')
        d = self.dialog
        self.assertEqual(d.editing, '既有書庫')
        self.assertFalse(d.raw_mode)
        self.assertFalse(d.name.isReadOnly())
        self.assertEqual(d.conditions.cellWidget(0, 2).text(), '科幻')
        d.conditions.cellWidget(0, 2).setText('歷史')
        with patch.object(ui, 'question_dialog', return_value=True), patch.object(ui, 'info_dialog'):
            d.create_libraries()
        saved = self.db.new_api.pref('virtual_libraries', {})
        self.assertEqual(set(saved), {'既有書庫', '保留'})
        self.assertEqual(saved['保留'], 'tags:true')
        self.assertIn('歷史', saved['既有書庫'])

    def test_advanced_preserved_and_cancel(self):
        search = '(tags:"=科幻" or tags:"=歷史") and not authors:"=作者乙"'
        self.load_existing('進階', search)
        d = self.dialog
        self.assertTrue(d.raw_mode)
        self.assertEqual(d.raw.toPlainText(), search)
        d.preview()
        self.assertEqual(d.rows[0][1], search)
        d.raw.setPlainText('tags:"=歷史"')
        d.reject()
        self.assertEqual(self.db.new_api.pref('virtual_libraries', {})['進階'], search)

    def test_external_edit_does_not_get_overwritten(self):
        self.load_existing('既有書庫', 'tags:"=科幻"')
        self.db.new_api.set_pref('virtual_libraries', {'既有書庫': 'tags:"=歷史"'})
        with patch.object(ui, 'error_dialog') as error:
            self.dialog.create_libraries()
        error.assert_called_once()
        self.assertEqual(self.db.new_api.pref('virtual_libraries', {})['既有書庫'], 'tags:"=歷史"')

    def test_discard_guard(self):
        self.load_existing('既有書庫', 'tags:"=科幻"')
        d = self.dialog
        d.conditions.cellWidget(0, 2).setText('歷史')
        with patch.object(ui, 'question_dialog', return_value=False):
            d.libraries.setCurrentRow(0)
        self.assertEqual(d.editing, '既有書庫')
        self.assertEqual(d.libraries.currentItem().data(Qt.ItemDataRole.UserRole), '既有書庫')

    def test_expression_round_trip(self):
        for term in ['科幻', 'a"b', 'a\\b', '=x', 'a (and b)']:
            for op in ['eq', 'contains']:
                search = core.expression([core.condition('tags', 'text', op, term)])
                parsed = core.editable_conditions(search, core.fields(self.db))
                self.assertEqual(parsed, ([('tags', op, term)], False))
        self.assertIsNone(core.editable_conditions('tags:~科.*', core.fields(self.db)))

    def test_simple_advanced_edit_and_round_trip(self):
        self.load_existing('既有書庫', 'tags:"=科幻"')
        d = self.dialog
        d.advanced.setChecked(True)
        self.assertTrue(d.raw_mode)
        self.assertIn('科幻', d.raw.toPlainText())
        d.raw.setPlainText('tags:"=歷史"')
        d.advanced.setChecked(False)
        self.assertFalse(d.raw_mode)
        self.assertEqual(d.conditions.cellWidget(0, 2).text(), '歷史')
        d.advanced.setChecked(True)
        d.raw.setPlainText('tags:"=歷史" and not authors:"=作者乙"')
        with patch.object(ui, 'question_dialog', return_value=True), patch.object(ui, 'info_dialog'):
            d.create_libraries()
        self.assertEqual(self.db.new_api.pref('virtual_libraries', {})['既有書庫'], 'tags:"=歷史" and not authors:"=作者乙"')

    def test_complex_advanced_cannot_be_dropped(self):
        search = '(tags:"=科幻" or tags:"=歷史") and not authors:"=作者乙"'
        self.load_existing('進階', search)
        with patch.object(ui, 'info_dialog') as info:
            self.dialog.advanced.setChecked(False)
        info.assert_called_once()
        self.assertTrue(self.dialog.raw_mode)
        self.assertTrue(self.dialog.advanced.isChecked())
        self.assertEqual(self.dialog.raw.toPlainText(), search)

    def test_new_advanced_does_not_overwrite_existing(self):
        d = self.dialog
        self.db.new_api.set_pref('virtual_libraries', {'已有': 'tags:"=科幻"'})
        d.advanced.setChecked(True)
        self.assertTrue(d.raw_mode)
        d.name.setText('已有')
        d.raw.setPlainText('tags:"=歷史"')
        with patch.object(ui, 'question_dialog') as confirm:
            d.create_libraries()
        confirm.assert_not_called()
        self.assertEqual(self.db.new_api.pref('virtual_libraries', {})['已有'], 'tags:"=科幻"')

    def test_delete_cancel_and_confirm(self):
        self.load_existing('既有書庫', 'tags:"=科幻"')
        before = self.db.new_api.all_book_ids()
        with patch.object(ui, 'question_dialog', return_value=False):
            self.dialog.delete_library()
        self.assertIn('既有書庫', self.db.new_api.pref('virtual_libraries', {}))
        self.gui._remove_vl.assert_not_called()
        with patch.object(ui, 'question_dialog', return_value=True):
            self.dialog.delete_library()
        self.assertEqual(self.db.new_api.pref('virtual_libraries', {}), {'保留': 'tags:true'})
        self.gui._remove_vl.assert_called_once_with('既有書庫', reapply=True)
        self.assertEqual(self.db.new_api.all_book_ids(), before)
        self.assertIsNone(self.dialog.editing)
        self.assertFalse(self.dialog.delete.isEnabled())

    def test_delete_rechecks_after_confirmation(self):
        self.load_existing('既有書庫', 'tags:"=科幻"')
        def changed(*args, **kwargs):
            self.db.new_api.set_pref('virtual_libraries', {'既有書庫': 'tags:"=歷史"'})
            return True
        with patch.object(ui, 'question_dialog', side_effect=changed), patch.object(ui, 'error_dialog') as error:
            self.dialog.delete_library()
        error.assert_called_once()
        self.gui._remove_vl.assert_not_called()
        self.assertEqual(self.db.new_api.pref('virtual_libraries', {})['既有書庫'], 'tags:"=歷史"')

    def test_delete_disabled_for_new_and_batch(self):
        self.assertFalse(self.dialog.delete.isEnabled())
        self.load_existing('既有書庫', 'tags:"=科幻"')
        self.assertTrue(self.dialog.delete.isEnabled())
        self.dialog.toggle_batch()
        self.assertFalse(self.dialog.delete.isEnabled())
        self.dialog.delete_library()
        self.gui._remove_vl.assert_not_called()

    def test_invalid_advanced_does_not_write(self):
        self.load_existing('既有書庫', 'tags:"=科幻"')
        d = self.dialog
        d.advanced.setChecked(True)
        d.raw.setPlainText('(')
        with patch.object(ui, 'error_dialog') as error:
            d.create_libraries()
        error.assert_called_once()
        self.assertEqual(self.db.new_api.pref('virtual_libraries', {})['既有書庫'], 'tags:"=科幻"')

    def test_order_move_preserves_draft_and_persists(self):
        self.load_existing('既有書庫', 'tags:"=科幻"')
        d = self.dialog
        before = self.db.new_api.pref('virtual_libraries', {})
        d.conditions.cellWidget(0, 2).setText('未存草稿')
        old = core.ordered_names(self.db)
        row = d.libraries.currentRow()
        delta = -1 if row > 1 else 1
        d.move_library(delta)
        self.assertEqual(d.conditions.cellWidget(0, 2).text(), '未存草稿')
        self.assertEqual(d.editing, '既有書庫')
        self.assertNotEqual(core.ordered_names(self.db), old)
        self.assertEqual(self.db.new_api.pref('virtual_libraries', {}), before)
        fresh = ui.BuilderDialog(self.gui)
        self.assertEqual([fresh.libraries.item(i).text() for i in range(1, fresh.libraries.count())], core.ordered_names(self.db))
        fresh.close()
        self.gui.rebuild_vl_tabs.assert_called_once()

    def test_order_boundaries_and_stale(self):
        self.load_existing('既有書庫', 'tags:"=科幻"')
        names = core.ordered_names(self.db)
        core.save_order(self.db, names, names)
        self.dialog.libraries.blockSignals(True)
        self.dialog.libraries.setCurrentRow(1)
        self.dialog.libraries.blockSignals(False)
        self.dialog.move_library(-1)
        self.assertEqual(core.ordered_names(self.db), names)
        self.db.new_api.set_pref('virt_libs_order', ['', *reversed(names)])
        with patch.object(ui, 'error_dialog') as error:
            self.dialog.move_library(1)
        error.assert_called_once()

    def test_rename_keeps_order_hidden_and_other_library(self):
        self.load_existing('既有書庫', 'tags:"=科幻"')
        self.db.new_api.set_pref('virt_libs_order', ['', '既有書庫', '保留'])
        self.db.new_api.set_pref('virt_libs_hidden', ['既有書庫'])
        self.db.new_api.set_pref('virtual_lib_on_startup', '既有書庫')
        self.dialog.name.setText('新名稱')
        with patch.object(ui, 'question_dialog', return_value=True), patch.object(ui, 'info_dialog'):
            self.dialog.create_libraries()
        saved = self.db.new_api.pref('virtual_libraries', {})
        self.assertEqual(set(saved), {'新名稱', '保留'})
        self.assertEqual(self.db.new_api.pref('virt_libs_order'), ['', '新名稱', '保留'])
        self.assertEqual(self.db.new_api.pref('virt_libs_hidden'), ['新名稱'])
        self.assertEqual(self.db.new_api.pref('virtual_lib_on_startup'), '新名稱')
        self.gui.virtual_libraries_changed.assert_called_once_with(renamed=(('既有書庫', '新名稱'),))

    def test_rename_collision_and_cancel(self):
        self.load_existing('既有書庫', 'tags:"=科幻"')
        before = dict(self.db.new_api.pref('virtual_libraries', {}))
        self.dialog.name.setText('保留')
        with patch.object(ui, 'error_dialog') as error:
            self.dialog.create_libraries()
        error.assert_called_once()
        self.assertEqual(self.db.new_api.pref('virtual_libraries', {}), before)
        self.dialog.name.setText('新名稱')
        self.dialog.reject()
        self.assertEqual(self.db.new_api.pref('virtual_libraries', {}), before)

    def test_helper_relative_date_and_comparison(self):
        term = core.advanced_condition('timestamp', 'datetime', 'recent_days', '30')
        self.assertEqual(term, 'date:>30_daysago')
        self.assertEqual(len(self.db.new_api.search(term)), 4)
        self.assertEqual(len(self.db.new_api.search(core.advanced_condition('timestamp', 'datetime', 'older_days', '30'))), 0)
        self.assertEqual(len(self.db.new_api.search(core.advanced_condition('timestamp', 'datetime', 'today', ''))), 4)
        self.assertEqual(len(self.db.new_api.search(core.advanced_condition('rating', 'rating', 'ge', '3'))), 0)
        with self.assertRaises(ValueError):
            core.advanced_condition('timestamp', 'datetime', 'recent_days', '-1')
        with self.assertRaises(Exception):
            core.advanced_condition('tags', 'text', 'regex', '[')

    def test_helper_combines_without_saving(self):
        from calibre_plugins.virtual_library_builder.query_helper import QueryHelper
        d = self.dialog
        d.advanced.setChecked(True)
        d.raw.setPlainText('tags:"=科幻"')
        h = QueryHelper(d)
        field, op, value = [h.table.cellWidget(0, i) for i in range(3)]
        field.setCurrentIndex(field.findData('tags'))
        value.setText('歷史')
        h.apply_expression()
        self.assertEqual(len(self.db.new_api.search(d.raw.toPlainText())), 1)
        self.assertEqual(self.db.new_api.pref('virtual_libraries', {}), {})
        h.close()
        before = d.raw.toPlainText()
        h = QueryHelper(d)
        h.reject()
        self.assertEqual(d.raw.toPlainText(), before)
        h.close()
        self.assertEqual(core.combine_search('tags:true', 'authors:true', 'or'), '(tags:true) or (authors:true)')
        self.assertEqual(core.combine_search('old', 'tags:true', 'replace'), 'tags:true')

    def test_mode_switch_keeps_window_and_editor_geometry(self):
        d = self.dialog
        d.name.setText('版面測試')
        d.conditions.cellWidget(0, 2).setText('科幻')
        d.show()
        self.app.processEvents()
        size = d.size()
        editor_rect = d.editor_stack.geometry()
        list_rect = d.libraries.geometry()
        bottom = d.batch_toggle.geometry()
        for advanced in (True, False, True, False):
            d.advanced.setChecked(advanced)
            self.app.processEvents()
            self.assertEqual(d.size(), size)
            self.assertEqual(d.editor_stack.geometry(), editor_rect)
            self.assertEqual(d.libraries.geometry(), list_rect)
            self.assertEqual(d.batch_toggle.geometry(), bottom)
        d.resize(d.width(), d.height() + 100)
        self.app.processEvents()
        self.assertGreater(d.height(), size.height())
        self.assertGreater(d.editor_stack.height(), editor_rect.height())

    def test_row_joins_are_left_to_right_and_reloadable(self):
        d = self.dialog
        d.name.setText('混合條件')
        for row, value in enumerate(['科幻', '歷史', '作者乙']):
            if row:
                d.add_condition()
            field = d.conditions.cellWidget(row, 0)
            field.setCurrentIndex(field.findData('authors' if row == 2 else 'tags'))
            d.conditions.cellWidget(row, 2).setText(value)
        d.conditions.cellWidget(1, 3).setCurrentIndex(1)
        search = d.inputs()[0][0][1]
        self.assertEqual(len(self.db.new_api.search(search)), 1)
        rows = core.editable_rows(search, d.metadata)
        self.assertEqual([row[3] for row in rows], ['and', 'or', 'and'])
        d.populate_conditions(rows)
        self.assertEqual(d.inputs()[0][0][1], search)
        self.assertFalse(d.conditions.cellWidget(0, 3).isEnabled())

    def test_main_form_has_relative_dates(self):
        d = self.dialog
        d.name.setText('最近加入')
        field, op, value = [d.conditions.cellWidget(0, col) for col in range(3)]
        field.setCurrentIndex(field.findData('timestamp'))
        op.setCurrentIndex(op.findData('recent_days'))
        value.setText('30')
        self.assertEqual(len(self.db.new_api.search(d.inputs()[0][0][1])), 4)
        parsed = core.editable_rows(d.inputs()[0][0][1], d.metadata)
        self.assertEqual(parsed[0][:3], ('timestamp', 'recent_days', '30'))

    def test_edit_save_has_no_redundant_confirmation(self):
        self.load_existing('既有書庫', 'tags:"=科幻"')
        self.dialog.conditions.cellWidget(0, 2).setText('歷史')
        with patch.object(ui, 'question_dialog') as question, patch.object(ui, 'info_dialog') as info:
            self.dialog.create_libraries()
        question.assert_not_called()
        info.assert_not_called()
        self.assertIn('歷史', self.db.new_api.pref('virtual_libraries', {})['既有書庫'])

    def test_full_operator_rows_round_trip(self):
        for field, datatype, op, value in [('tags', 'text', 'ne', '科幻'), ('tags', 'text', 'not_contains', '幻'), ('tags', 'text', 'regex', '科.*'), ('rating', 'rating', 'ge', '3'), ('rating', 'rating', 'le', '4')]:
            term = core.advanced_condition(field, datatype, op, value)
            parsed = core.editable_rows(core.row_expression([term], ['and']), self.dialog.metadata)
            self.assertEqual(parsed, [(field, op, value, 'and')])


if __name__ == '__main__':
    result = unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
    raise SystemExit(not result.wasSuccessful())
