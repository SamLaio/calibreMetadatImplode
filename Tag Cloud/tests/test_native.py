"""Launch the packaged plugin in an isolated calibre main window."""
import json
import traceback
import os
from pathlib import Path

from calibre.utils.config import config_dir, prefs
from calibre.db.legacy import LibraryDatabase
from calibre.ebooks.metadata.book.base import Metadata

root = Path(__file__).parents[2]
profile = Path(config_dir)
if not profile.resolve().is_relative_to((root / 'dist').resolve()):
    raise RuntimeError('測試僅能使用 dist 下的隔離設定。')
library = profile / 'Library'
db = LibraryDatabase(str(library))
for index in range(60 if not db.new_api.all_book_ids() else 0):
    mi = Metadata('測試書籍 ' + str(index), ['作者' + str(index % 6)])
    mi.tags = ['歷史', '台灣'] if index % 3 else ['科幻', '推理', '文學']
    mi.series = '測試系列 ' + str(index % 4)
    db.create_book_entry(mi)
db.close()
prefs['library_path'] = str(library)
prefs['language'] = 'zh_TW'
from calibre.customize.ui import add_plugin
packages = ([root / 'dist' / 'TagCloud.zip', root / 'dist' / 'EpubSplit-zh_TW-release.zip']
            if not os.environ.get('TAG_CLOUD_TEST_ALL_PLUGINS') else sorted((root / 'dist').glob('*.zip')))
for package in packages:
    add_plugin(str(package))
from calibre.gui2 import gprefs
gprefs['action-layout-toolbar'] = tuple(gprefs['action-layout-toolbar']) + ('Tag Cloud', 'EpubSplit')
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
        from calibre.customize import InterfaceActionBase
        from calibre.customize.zipplugin import loader
        declarations = [loader.load(str(package)) for package in packages]
        expected_actions = [declaration.name for declaration in declarations
                            if issubclass(declaration, InterfaceActionBase)]
        assert all(name in gui.iactions for name in expected_actions), expected_actions
        action = gui.iactions['Tag Cloud']
        assert not gui.iactions['EpubSplit'].qaction.icon().isNull()
        assert 'EpubSplit' in gprefs['action-layout-toolbar']
        assert 'Tag Cloud' not in gprefs['action-layout-toolbar']
        panel = action.panel
        if os.environ.get('TAG_CLOUD_FLOAT_RESTART'):
            assert action.display_mode() == 'floating'
            window = action.presentation.window
            assert window.isVisible() and panel.parentWidget() is window
            assert window.width() == 640 and window.height() == 520
            assert action.qaction.isChecked()
            (profile / 'restart-result.json').write_text(json.dumps({'success': True, 'width': window.width(),
                                                                    'height': window.height()}), encoding='utf-8')
            gui.quit()
            return
        assert action.qaction.isEnabled() and panel.isVisible()
        assert not action.qaction.isVisible()
        assert action.sidebar.button.isVisible()
        assert action.splitter.widget(0) is action.tree_pane
        assert action.tree_pane.layout().indexOf(gui.tb_widget.tb_bar) == 1
        assert dict(panel.counts)['歷史'] == 40
        panel.clicked(QUrl('tag:' + str(panel.names.index('歷史'))))
        assert len(gui.current_db.new_api.search(gui.search.currentText())) == 40
        panel.field.setCurrentIndex(panel.field.findData('authors'))
        assert len(panel.counts) == 6
        panel.field.setCurrentIndex(panel.field.findData('tags'))
        central = gui.layout_container
        for tree, cloud in ((True, True), (False, True), (True, False), (False, False), (False, True), (True, True)):
            central.tag_browser_button.setChecked(tree)
            action.sidebar.button.setChecked(cloud)
            central.relayout()
            app.processEvents()
            assert central.is_visible.tag_browser == tree
            assert central.tag_browser.isVisible() == (tree or cloud)
            assert gui.tags_view.isVisible() == tree
            assert gui.tb_widget.tb_bar.isVisible() == tree
            assert panel.isVisible() == cloud
            assert action.qaction.isChecked() == cloud
        central.tag_browser_button.setChecked(False)
        central.relayout()
        from qt.core import QPointF
        central.wide_move_splitter_handle_to(central.left_handle, QPointF(300, 0))
        central.relayout()
        assert not central.is_visible.tag_browser
        assert panel.isVisible() and central.tag_browser.width() > 100
        assert not central.serialized_settings()['wide_visibility']['tag_browser']
        central.change_layout(gui, False)
        central.tag_browser_button.setChecked(False)
        central.relayout()
        assert panel.isVisible() and not gui.tags_view.isVisible()
        assert central.tag_browser.width() > 100
        central.change_layout(gui, True)
        central.tag_browser_button.setChecked(True)
        panel.limit.setCurrentText('全部')
        assert len(panel.names) == len(panel.counts)
        if os.environ.get('TAG_CLOUD_TEST_FLOATING'):
            from qt.core import QKeySequence, QKeyEvent, QEvent, Qt, QWidget
            assert 'tag_cloud_toggle_floating' in gui.keyboard.shortcuts
            assert action.floating_action.shortcut().isEmpty()
            panel.selected = ['歷史']
            panel.apply_search()
            search = gui.search.currentText()
            action.floating_action.setShortcut(QKeySequence('Ctrl+Alt+Shift+F12'))
            gui.activateWindow()
            app.processEvents()
            modifiers = Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.AltModifier | Qt.KeyboardModifier.ShiftModifier
            def key_click(widget):
                app.sendEvent(widget, QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_F12, modifiers))
                app.sendEvent(widget, QKeyEvent(QEvent.Type.KeyRelease, Qt.Key.Key_F12, modifiers))
            action.set_display_mode('sidebar')
            action.qaction.setChecked(True)
            key_click(gui)
            app.processEvents()
            assert not action.qaction.isChecked() and action.display_mode() == 'sidebar'
            key_click(gui)
            app.processEvents()
            assert action.qaction.isChecked() and action.display_mode() == 'sidebar'
            assert panel.parentWidget() is action.splitter
            action.set_display_mode('floating')
            window = action.presentation.window
            assert action.display_mode() == 'floating' and window.isVisible()
            assert panel.parentWidget() is window
            assert panel.selected == ['歷史'] and gui.search.currentText() == search
            central.tag_browser_button.setChecked(False)
            central.relayout()
            assert not central.tag_browser.isVisible() and window.isVisible()
            window.activateWindow()
            app.processEvents()
            key_click(window)
            app.processEvents()
            assert not window.isVisible()
            gui.activateWindow()
            app.processEvents()
            key_click(gui)
            app.processEvents()
            assert window.isVisible()
            window.close()
            assert not action.qaction.isChecked() and panel.selected == ['歷史']
            action.toggle_cloud()
            action.set_display_mode('sidebar')
            assert action.splitter.widget(1) is panel and not window.isVisible()
            preferences_checked = []
            check_timer = QTimer()
            check_timer.setInterval(40)
            def check_preferences():
                dialog = app.activeModalWidget()
                if dialog is not None:
                    modules = [type(widget).__module__ for widget in dialog.findChildren(QWidget)]
                    if any('keyboard' in module for module in modules):
                        preferences_checked.append(True)
                        dialog.reject()
                        check_timer.stop()
            check_timer.timeout.connect(check_preferences)
            check_timer.start()
            def cancel_preferences():
                check_timer.stop()
                dialog = app.activeModalWidget()
                if dialog is not None:
                    dialog.reject()
            QTimer.singleShot(5000, cancel_preferences)
            action.configure_cloud_shortcut()
            assert preferences_checked
            action.set_display_mode('floating')
            window.resize(640, 520)
            window.move(80, 60)
            window.save_geometry()
            app.processEvents()
            window.grab().save(str(root / 'dist' / 'tag-cloud-floating.png'))
        if os.environ.get('TAG_CLOUD_TEST_EDITS'):
            from calibre_plugins.tag_cloud import context
            from qt.core import QDialogButtonBox
            def confirmed_operation(remove=False):
                term = '原生測試標籤' if remove else '歷史'
                ids = set(panel.term_books[term])
                timer = QTimer()
                timer.setInterval(30)
                def respond():
                    dialog = app.activeModalWidget()
                    if isinstance(dialog, context.ValueDialog):
                        dialog.editor.setText('原生測試標籤')
                        dialog.accept()
                    elif dialog is not None:
                        buttons = dialog.findChild(QDialogButtonBox)
                        yes = buttons.button(QDialogButtonBox.StandardButton.Yes) if buttons else None
                        if yes is not None:
                            dialog.grab().save(str(root / 'dist' / 'tag-cloud-edit-confirm.png'))
                            yes.click()
                            timer.stop()
                timer.timeout.connect(respond)
                timer.start()
                def timeout():
                    timer.stop()
                    dialog = app.activeModalWidget()
                    if dialog is not None:
                        dialog.reject()
                QTimer.singleShot(5000, timeout)
                context.edit_term(panel, term, 'tags', gui.current_db, ids, remove=remove)
                timer.stop()
                return ids
            ids = confirmed_operation()
            assert all('原生測試標籤' in gui.current_db.new_api.field_for('tags', book_id) for book_id in ids)
            assert all('台灣' in gui.current_db.new_api.field_for('tags', book_id) for book_id in ids)
            confirmed_operation(remove=True)
            assert all('原生測試標籤' not in gui.current_db.new_api.field_for('tags', book_id) for book_id in ids)
            assert all('台灣' in gui.current_db.new_api.field_for('tags', book_id) for book_id in ids)
        gui.resize(1400, 900)
        action.splitter.setSizes([450, 320])
        app.processEvents()
        gui.grab().save(str(root / 'dist' / 'tag-cloud-native.png'))
        result = {'success': True, 'checks': ['package load', 'four visibility states', 'bottom button', 'cloud-only resize', 'all words', 'tag search', 'authors', 'render']}
        result['packages'] = len(packages)
        result['interface_actions'] = expected_actions
        if os.environ.get('TAG_CLOUD_TEST_FLOATING'):
            result['checks'].extend(['floating panel transfer', 'real shortcut key', 'native shortcut preferences',
                                     'selection preserved', 'sidebar hidden when floating', 'window close hides'])
        if os.environ.get('TAG_CLOUD_TEST_EDITS'):
            result['checks'].extend(['native edit dialog', 'native confirmation', 'metadata rename',
                                     'metadata removal', 'unrelated values preserved'])
    except Exception:
        result = {'success': False, 'error': traceback.format_exc()}
    (profile / 'result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    gui.quit()


QTimer.singleShot(6500, verify)
run_gui_(opts, args, app)
