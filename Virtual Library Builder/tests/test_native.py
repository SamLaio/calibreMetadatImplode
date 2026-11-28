import os, json, traceback
from pathlib import Path
from unittest.mock import patch
from calibre.utils.config import config_dir, prefs
from calibre.db.legacy import LibraryDatabase
from calibre.ebooks.metadata.book.base import Metadata
root = Path(__file__).parents[2]
profile = Path(config_dir)
if not profile.resolve().is_relative_to((root / 'dist').resolve()):
    raise RuntimeError('測試只允許 dist 隔離設定。')
library = profile / 'Library'
db = LibraryDatabase(str(library))
if not db.new_api.all_book_ids():
    for title, tags in [('甲', ['科幻']), ('乙', ['歷史']), ('丙', ['科幻', '歷史'])]:
        mi = Metadata(title, ['測試作者'])
        mi.tags = tags
        db.create_book_entry(mi)
db.close()
prefs['library_path'] = str(library)
prefs['language'] = 'zh_TW'
from calibre.customize.ui import add_plugin
add_plugin(str(root / 'dist' / 'VirtualLibraryBuilder.zip'))
from calibre.gui2 import gprefs
gprefs['action-layout-toolbar'] = tuple(gprefs['action-layout-toolbar']) + ('Virtual Library Builder',)
from calibre.utils.localization import set_translators
set_translators()
from calibre.gui2 import dynamic
dynamic.set('welcome_wizard_was_run', True)
from calibre.gui2.main import init_qt, option_parser, run_gui_
from calibre.gui2.ui import get_gui
from qt.core import QTimer, QUrl, QFontDatabase, QFont

app, _, _ = init_qt(['calibre'])
font_file = Path('C:/Windows/Fonts/msjh.ttc')
if font_file.exists():
    font_id = QFontDatabase.addApplicationFont(str(font_file))
    families = QFontDatabase.applicationFontFamilies(font_id)
    if families:
        app.setFont(QFont(families[0], 10))
opts, args = option_parser().parse_args(['--with-library', str(library), '--no-update-check'])


def verify():
    gui = get_gui()
    try:
        from calibre_plugins.virtual_library_builder import ui
        assert 'Virtual Library Builder' in gui.iactions
        assert gui.iactions['Virtual Library Builder'].qaction.text() == '書庫建立器'
        assert not gui.iactions['Virtual Library Builder'].qaction.icon().isNull()
        action = gui.iactions['Virtual Library Builder']
        assert 'Library Condition Filter' not in gui.iactions
        assert action.popup_type == ui.QToolButton.ToolButtonPopupMode.MenuButtonPopup
        assert '條件篩選器' in [a.text() for a in action.qaction.menu().actions()]
        if not os.environ.get('VLB_RESTART'):
            assert 'library_builder_quick_find' in gui.keyboard.shortcuts
            assert action.find_action.shortcut().isEmpty()
            action.find_action.trigger()
            find = action.quick_find_dialog
            find.field.setCurrentIndex(find.field.findData('title'))
            find.text.setText('甲')
            find.search()
            app.processEvents()
            assert find.isVisible() and not find.isModal()
            assert gui.library_view.model().rowCount() == 1
            action.show_find()
            assert action.quick_find_dialog is find
            assert find.text.selectedText() == '甲'
            find.close()
            gui.search.set_search_string('')
            with patch.object(ui, 'BuilderDialog') as builder:
                action.qaction.trigger()
                builder.assert_called_once_with(gui)
                builder.return_value.exec.assert_called_once()
            with patch('calibre_plugins.virtual_library_builder.query_helper.QueryHelper') as helper:
                action.filter_action.trigger()
                helper.assert_called_once_with(gui=gui)
                helper.return_value.show.assert_called_once()
                helper.return_value.exec.assert_not_called()
            action.search_filter_dialog = None
            action.show_filter()
            floating_filter = action.search_filter_dialog
            app.processEvents()
            assert floating_filter.isVisible() and not floating_filter.isModal()
            assert app.activeModalWidget() is None
            action.show_filter()
            assert action.search_filter_dialog is floating_filter
            # Selection in the main book view must remain usable while the filter is open.
            gui.library_view.setCurrentIndex(gui.library_view.model().index(1, 0))
            assert gui.library_view.currentIndex().row() == 1
            floating_filter.close()
            from calibre_plugins.virtual_library_builder.query_helper import QueryHelper
            gui.search.set_search_string('authors:"=測試作者"')
            gui.apply_virtual_library(None)
            existing_libraries = dict(gui.current_db.new_api.pref('virtual_libraries', {}))
            search_filter = QueryHelper(gui=gui)
            search_filter.show()
            search_filter.table.cellWidget(0, 2).setText('科幻')
            search_filter.apply_expression()
            app.processEvents()
            assert gui.library_view.model().rowCount() == 2
            assert 'authors:' in gui.search.currentText() and '科幻' in gui.search.currentText()
            assert search_filter.isVisible()
            applied = gui.search.currentText()
            search_filter.close()
            reopened_filter = QueryHelper(gui=gui)
            assert reopened_filter.table.cellWidget(0, 2).text() == '科幻'
            reopened_filter.apply_expression()
            assert gui.search.currentText() == applied
            reopened_filter.close()
            assert gui.current_db.new_api.pref('virtual_libraries', {}) == existing_libraries
            from qt.core import QInputDialog
            def enter_library_name():
                dialog = app.activeModalWidget()
                assert isinstance(dialog, QInputDialog)
                dialog.setTextValue('篩選另存測試')
                dialog.accept()
            QTimer.singleShot(25, enter_library_name)
            search_filter.create_library_button.click()
            assert '篩選另存測試' in gui.current_db.new_api.pref('virtual_libraries', {})
            assert search_filter.isVisible()
            assert len(gui.current_db.new_api.search(gui.current_db.new_api.pref('virtual_libraries', {})['篩選另存測試'])) == 2
            gui._remove_vl('篩選另存測試', reapply=True)

            gui.add_virtual_library(gui.current_db, '範圍測試', 'tags:"=科幻"')
            gui.apply_virtual_library('範圍測試')
            limited_filter = QueryHelper(gui=gui)
            limited_filter.table.cellWidget(0, 2).setText('歷史')
            limited_filter.join.setCurrentIndex(2)
            limited_filter.apply_expression()
            app.processEvents()
            assert gui.current_db.data.get_base_restriction_name() == '範圍測試'
            assert gui.library_view.model().rowCount() == 1
            gui._remove_vl('範圍測試', reapply=True)
            gui.search.set_search_string('')
        if os.environ.get('VLB_RESTART'):
            from calibre_plugins.virtual_library_builder.query_helper import QueryHelper
            fresh_filter = QueryHelper(gui=gui)
            assert fresh_filter.table.rowCount() == 1
            assert fresh_filter.table.cellWidget(0, 2).text() == ''
            fresh_filter.close()
            saved = gui.current_db.new_api.pref('virtual_libraries', {})
            assert '刪除測試' not in saved
            assert '更名測試書庫' in saved
            assert '歷史' in saved['更名測試書庫']
            gui.apply_virtual_library('更名測試書庫')
            assert gui.library_view.model().rowCount() == 2
            expected_order = json.loads((profile / 'order.json').read_text(encoding='utf-8'))
            assert ui.core.ordered_names(gui.current_db) == expected_order
            assert [gui.vl_tabs.tabData(i) for i in range(gui.vl_tabs.count()) if gui.vl_tabs.tabData(i)] == expected_order
            result = {'success': True, 'restart': True, 'order': expected_order}
        else:
            d = ui.BuilderDialog(gui)
            assert d.windowTitle() == '書庫建立器 0.1.12'
            assert not d.windowIcon().isNull()
            gui.grab().save(str(root / 'dist' / 'library-builder-toolbar.png'))
            d.show()
            d.name.setText('測試科幻書庫')
            field = d.conditions.cellWidget(0, 0)
            field.setCurrentIndex(field.findData('tags'))
            d.conditions.cellWidget(0, 2).setText('科幻')
            d.preview()
            assert d.rows[0][2] == 2
            app.processEvents()
            geometry = (d.size(), d.editor_stack.geometry(), d.libraries.geometry(), d.batch_toggle.geometry())
            for advanced in (True, False, True, False):
                d.advanced.setChecked(advanced)
                app.processEvents()
                assert (d.size(), d.editor_stack.geometry(), d.libraries.geometry(), d.batch_toggle.geometry()) == geometry
            d.grab().save(str(root / 'dist' / 'virtual-library-builder.png'))
            d.activate.setChecked(True)
            with patch.object(ui, 'question_dialog', return_value=True), patch.object(ui, 'info_dialog'):
                d.create_libraries()
            assert gui.current_db.data.get_base_restriction_name() == '測試科幻書庫'
            assert gui.library_view.model().rowCount() == 2
            batch = ui.BuilderDialog(gui)
            batch.toggle_batch()
            batch.filter.setText('歷史')
            batch.check_values(True)
            batch.preview()
            assert batch.rows[0][2] == 2  # Entire DB, not restricted to current VL.
            with patch.object(ui, 'question_dialog', return_value=True), patch.object(ui, 'info_dialog'):
                batch.create_libraries()
            assert len(gui.current_db.new_api.pref('virtual_libraries', {})) == 2
            edit = ui.BuilderDialog(gui)
            for row in range(edit.libraries.count()):
                if edit.libraries.item(row).data(ui.Qt.ItemDataRole.UserRole) == '測試科幻書庫':
                    edit.libraries.setCurrentRow(row)
                    break
            assert edit.editing == '測試科幻書庫' and not edit.raw_mode
            edit.conditions.cellWidget(0, 2).setText('歷史')
            edit.advanced.setChecked(True)
            assert edit.raw_mode and '歷史' in edit.raw.toPlainText()
            edit.raw.setPlainText('tags:"=歷史" and not title:"=不存在"')
            edit.show()
            app.processEvents()
            edit.grab().save(str(root / 'dist' / 'virtual-library-builder.png'))
            with patch.object(ui, 'question_dialog', return_value=True), patch.object(ui, 'info_dialog'):
                edit.create_libraries()
            saved = gui.current_db.new_api.pref('virtual_libraries', {})
            assert len(saved) == 2 and '歷史' in saved['測試科幻書庫']
            assert gui.library_view.model().rowCount() == 2
            rename = ui.BuilderDialog(gui)
            for row in range(rename.libraries.count()):
                if rename.libraries.item(row).data(ui.Qt.ItemDataRole.UserRole) == '測試科幻書庫':
                    rename.libraries.setCurrentRow(row)
                    break
            rename.name.setText('更名測試書庫')
            with patch.object(ui, 'question_dialog', return_value=True), patch.object(ui, 'info_dialog'):
                rename.create_libraries()
            saved = gui.current_db.new_api.pref('virtual_libraries', {})
            assert '測試科幻書庫' not in saved and '更名測試書庫' in saved and len(saved) == 2
            assert gui.current_db.data.get_base_restriction_name() == '更名測試書庫'
            order_dialog = ui.BuilderDialog(gui)
            order_dialog.libraries.setCurrentRow(1)
            first = order_dialog.libraries.currentItem().text()
            order_dialog.move_library(1)
            expected_order = [order_dialog.libraries.item(i).text() for i in range(1, order_dialog.libraries.count())]
            actual_tabs = [gui.vl_tabs.tabData(i) for i in range(gui.vl_tabs.count()) if gui.vl_tabs.tabData(i)]
            assert expected_order == actual_tabs
            (profile / 'order.json').write_text(json.dumps(expected_order, ensure_ascii=False), encoding='utf-8')
            assert order_dialog.libraries.currentItem().text() == first
            from calibre_plugins.virtual_library_builder.query_helper import QueryHelper
            order_dialog.advanced.setChecked(True)
            helper = QueryHelper(order_dialog)
            field, op, value = [helper.table.cellWidget(0, col) for col in range(3)]
            field.setCurrentIndex(field.findData('timestamp'))
            op.setCurrentIndex(op.findData('recent_days'))
            value.setText('30')
            helper.show()
            app.processEvents()
            helper.grab().save(str(root / 'dist' / 'virtual-library-query-helper.png'))
            original = order_dialog.raw.toPlainText()
            helper.apply_expression()
            assert original in order_dialog.raw.toPlainText() and '30_daysago' in order_dialog.raw.toPlainText()
            assert gui.current_db.new_api.pref('virtual_libraries', {}) == saved
            order_dialog.show()
            app.processEvents()
            order_dialog.grab().save(str(root / 'dist' / 'virtual-library-builder.png'))
            order_dialog.close()
            gui.add_virtual_library(gui.current_db, '刪除測試', 'tags:"=科幻"')
            gui.apply_virtual_library('刪除測試')
            remove = ui.BuilderDialog(gui)
            for row in range(remove.libraries.count()):
                if remove.libraries.item(row).data(ui.Qt.ItemDataRole.UserRole) == '刪除測試':
                    remove.libraries.setCurrentRow(row)
                    break
            before = gui.current_db.new_api.all_book_ids()
            with patch.object(ui, 'question_dialog', return_value=True):
                remove.delete_library()
            assert '刪除測試' not in gui.current_db.new_api.pref('virtual_libraries', {})
            assert gui.current_db.new_api.all_book_ids() == before
            assert not gui.current_db.data.get_base_restriction_name()
            assert gui.library_view.model().rowCount() == len(before)
            assert not remove.delete.isEnabled()
            remove.close()
            gui.virtual_library_menu_about_to_show()
            assert any(a.text() == '測試科幻書庫' for a in gui.virtual_library_menu.actions())
            result = {'success': True, 'checks': ['package load', 'toolbar icon', 'condition preview', 'native VL creation', 'native switch', 'batch entire library', 'native menu', 'load existing', 'edit existing without duplicate', 'advanced expression edit', 'delete active VL without deleting books', 'rename active VL', 'native tab ordering', 'relative date helper', 'stable mode geometry', 'split toolbar action routing', 'native search filter', 'virtual library scope retained', 'filter stays open', 'filter restores conditions', 'non-modal filter', 'main view remains usable', 'single filter window', 'create library from filter', 'native name dialog', 'quick find shortcut registration', 'quick find search', 'quick find single window']}
    except Exception:
        result = {'success': False, 'error': traceback.format_exc()}
    (profile / ('restart-result.json' if os.environ.get('VLB_RESTART') else 'result.json')).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    gui.quit()
QTimer.singleShot(6500, verify)
run_gui_(opts, args, app)
