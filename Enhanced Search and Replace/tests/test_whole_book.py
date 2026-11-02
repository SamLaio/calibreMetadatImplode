from test_support import scan
from pathlib import Path
from tempfile import TemporaryDirectory, mkdtemp
from types import SimpleNamespace
from unittest.mock import patch

from calibre.gui2 import Application
from calibre.gui2.tweak_book import editors, current_container, set_current_container
from calibre.gui2.tweak_book.boss import Boss
from calibre.gui2.tweak_book.editor.widget import Editor
from calibre.gui2.tweak_book.undo import GlobalUndoHistory
from calibre.ebooks.oeb.polish.container import get_container
from calibre.customize.ui import all_edit_book_tool_plugins
from calibre.gui2.tweak_book.plugin import load_plugin_tools
from qt.core import QWidget, Qt

app = Application([])
root = Path(__file__).resolve().parents[2]
plugin = next(p for p in all_edit_book_tool_plugins() if p.name == 'Enhanced Search and Replace')
list(load_plugin_tools(plugin))
from calibre_plugins.text_regex_p0.main import SearchDialog


class Host:
    @property
    def current_container(self):
        return current_container()


with TemporaryDirectory(dir=root/'dist', prefix='whole-book-') as temporary:
    c = get_container(str(root/'dist/text-regex-p0-fixture.epub'))
    second = '<html xmlns="http://www.w3.org/1999/xhtml"><body><p>第99章</p></body></html>'
    c.add_file('OEBPS/second.xhtml', second.encode('utf-8'), media_type='application/xhtml+xml', spine_index=1)
    c.add_file('OEBPS/style.css', b'p {color: red}', media_type='text/css')
    set_current_container(c)
    host = Host()
    host.gui = QWidget()
    host.gui.central = SimpleNamespace(current_editor=None)
    boss = host.boss = SimpleNamespace(global_undo=GlobalUndoHistory())
    boss.global_undo.open_book(c)
    boss.mkdtemp = lambda: mkdtemp(dir=temporary)
    boss.update_global_history_actions = lambda: None
    boss.commit_editor_to_container = lambda name: Boss.commit_editor_to_container(boss, name)
    boss.commit_all_editors_to_container = lambda: Boss.commit_all_editors_to_container(boss)
    boss.add_savepoint = lambda message: Boss.add_savepoint(boss, message)
    boss.rewind_savepoint = lambda: Boss.rewind_savepoint(boss)
    boss.apply_container_update_to_gui = lambda: Boss.update_editors_from_container(boss)
    boss.show_editor = lambda name: None

    def edit_file(name, syntax='html'):
        if name not in editors:
            ed = editors[name] = Editor(syntax)
            ed.data = current_container().raw_data(name)
        return editors[name]

    boss.edit_file = edit_file
    d = SearchDialog(host)
    d.pattern.setText(r'第(\d+)章')
    d.template.setText('第$1回')
    scan(d)
    assert len(d.rows) == 6 and not editors
    assert {row['name'] for row in d.rows} == {'OEBPS/chapter.xhtml', 'OEBPS/second.xhtml'}
    assert d.model.data(d.model.index(5,5)) == 'OEBPS/second.xhtml'
    d.select_row(5, 1)
    d.single()
    assert '第99回' in str(editors['OEBPS/second.xhtml'].editor.toPlainText())
    editors['OEBPS/second.xhtml'].undo()
    assert str(editors['OEBPS/second.xhtml'].editor.toPlainText()) == second
    boss.commit_all_editors_to_container()
    editors.clear()
    css = edit_file('OEBPS/style.css', syntax='css')
    host.gui.central.current_editor = css
    scan(d)
    assert len(d.rows) == 6
    d.select_row(5, 1)
    d.locate()
    ed = editors['OEBPS/second.xhtml']
    assert ed.editor.textCursor().selectedText() == '第99章'
    ed.replace_data(second.replace('99', '100'))
    scan(d)
    assert d.rows[-1]['before'] == '第100章'
    ed.replace_data(second.replace('99', '101'))
    try:
        d.apply([d.rows[-1]])
    except ValueError as err:
        assert '內容已變更' in str(err)
    else:
        raise AssertionError('stale unopened-file result accepted')
    ed.replace_data(second)
    scan(d)
    before = {name: d.read_source(name) for name in d.snapshots}
    safe = [row for row in d.rows if row['safe']]
    retained_rows = d.rows
    d.apply(safe)
    assert d.rows is retained_rows and len(d.rows)==6
    assert all(row['done'] for row in safe)
    assert all(d.model.data(d.model.index(i,4))=='已取代' for i,row in enumerate(d.rows) if row.get('done'))
    assert boss.global_undo.pos == 1
    assert '第99回' in current_container().raw_data('OEBPS/second.xhtml')
    assert '第12回' in current_container().raw_data('OEBPS/chapter.xhtml')
    assert '第99回' in str(ed.editor.toPlainText())
    set_current_container(boss.global_undo.undo())
    boss.apply_container_update_to_gui()
    assert all(d.read_source(name) == raw for name, raw in before.items())
    set_current_container(boss.global_undo.redo())
    boss.apply_container_update_to_gui()
    assert '第99回' in str(ed.editor.toPlainText())
    set_current_container(boss.global_undo.undo())
    boss.apply_container_update_to_gui()
    scan(d)
    for i, row in enumerate(d.rows):
        if row['safe']:
            d.model.setData(d.model.index(i,0), Qt.CheckState.Checked, Qt.ItemDataRole.CheckStateRole)
    saved_rows = d.rows
    saved_position = boss.global_undo.pos
    from calibre.ebooks.oeb.polish.container import Container
    original_open = Container.open

    def fail_second(self, name, mode='rb'):
        if name == 'OEBPS/second.xhtml' and mode == 'wb' and self is not d.container:
            raise OSError('測試第二檔寫入失敗')
        return original_open(self, name, mode)

    with patch.object(Container, 'open', fail_second):
        with patch('calibre_plugins.text_regex_p0.main.QMessageBox.warning') as warning:
            d.guard(d.batch)
            assert '已整批回復' in warning.call_args.args[2]
            assert 'second.xhtml' in warning.call_args.args[2]
    assert boss.global_undo.pos == saved_position
    assert all(d.read_source(name) == raw for name, raw in before.items())
    assert d.rows is saved_rows and d.model.data(d.model.index(5,0), Qt.ItemDataRole.CheckStateRole) == Qt.CheckState.Checked
    assert '取代失敗' in d.model.data(d.model.index(5,4))
    d.pattern.setText('第12章|Regex P0 Fixture');d.template.setText('新名稱');scan(d)
    assert any(row['name'] == current_container().opf_name for row in d.rows)
    d.apply(list(d.rows))
    assert '新名稱' in current_container().raw_data(current_container().opf_name)
    assert '新名稱' in current_container().raw_data('OEBPS/chapter.xhtml')
    set_current_container(boss.global_undo.undo())
    boss.apply_container_update_to_gui()
    assert 'Regex P0 Fixture' in current_container().raw_data(current_container().opf_name)
    d.pattern.setText(r'第(\d+)章');d.template.setText('第$1回')
    current_container().add_file('OEBPS/broken.xhtml', b'<html><body>', media_type='application/xhtml+xml')
    with patch('calibre_plugins.text_regex_p0.main.QMessageBox.warning') as warning:
        d.guard(lambda: scan(d))
        assert 'broken.xhtml' in warning.call_args.args[2]
    assert len(d.rows) == 7 and any(row['before'] == '第99章' for row in d.rows)
    assert any(row['name'] == 'OEBPS/broken.xhtml' and not row['safe'] for row in d.rows)
    d.close()
    editors.clear()

print('PASS whole book: no open chapter, CSS tab, unsaved source, locate, stale rejection, native checkpoint Undo/Redo, rollback and retained failures')
