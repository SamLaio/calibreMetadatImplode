from test_support import scan
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from calibre.gui2 import Application
from calibre.gui2.tweak_book import editors, set_current_container
from calibre.gui2.tweak_book.boss import Boss
from calibre.gui2.tweak_book.editor.widget import Editor
from calibre.ebooks.oeb.polish.container import get_container
from calibre.customize.ui import all_edit_book_tool_plugins
from calibre.gui2.tweak_book.plugin import load_plugin_tools
from qt.core import QWidget

app = Application([])
root = Path(__file__).resolve().parents[2]
plugin = next(p for p in all_edit_book_tool_plugins() if p.name == 'Enhanced Search and Replace')
list(load_plugin_tools(plugin))
from calibre_plugins.text_regex_p0.main import SearchDialog, text_syntax
from calibre_plugins.text_regex_p0.core import search, replace

c = get_container(str(root/'dist/text-regex-p0-fixture.epub'))
files = {
    'OEBPS/style.css': (b'p {color:red}', 'text/css'),
    'OEBPS/script.js': (b'const color="red";', 'application/javascript'),
    'OEBPS/note.txt': (b'color:red', 'text/plain'),
    'OEBPS/settings.json': (b'{"color":"red"}', 'application/json'),
    'OEBPS/image.svg': (b'<svg xmlns="http://www.w3.org/2000/svg"><text>red</text></svg>', 'image/svg+xml'),
    'OEBPS/cover.png': (b'\x89PNG\x00red', 'image/png'),
    'OEBPS/font.ttf': (b'\x00\x01\x00\x00red', 'font/ttf'),
}
for name, (data, mime) in files.items():
    c.add_file(name, data, media_type=mime)
set_current_container(c)
gui = QWidget()
gui.file_list = SimpleNamespace(build=lambda container: None)
boss = SimpleNamespace(gui=gui)
boss.commit_editor_to_container = lambda name: Boss.commit_editor_to_container(boss, name)
boss.commit_all_editors_to_container = lambda: Boss.commit_all_editors_to_container(boss)


def edit_file(name, syntax='html'):
    if name not in editors:
        ed = editors[name] = Editor(syntax)
        data = c.raw_data(name)
        ed.data = data.decode('utf-8') if isinstance(data, bytes) else data
    return editors[name]


boss.edit_file = edit_file
d = SearchDialog(SimpleNamespace(gui=gui, boss=boss, current_container=c))
assert {'OPF', 'NCX', 'XHTML', 'CSS', 'JS', 'TXT', 'JSON', 'SVG'} <= set(d.type_actions)
assert all(action.isChecked() for action in d.type_actions.values())
assert 'PNG' not in d.type_actions and 'TTF' not in d.type_actions
assert text_syntax('x.bin', 'application/octet-stream') is None
assert text_syntax('x.md', 'text/markdown') == 'text'
d.pattern.setText('red');d.template.setText('blue');scan(d)
assert {row['name'] for row in d.rows} == set(files) - {'OEBPS/cover.png', 'OEBPS/font.ttf'}
d.set_types(False)
assert not d.rows
with patch('calibre_plugins.text_regex_p0.main.QMessageBox.warning') as warning:
    d.guard(lambda: scan(d))
    assert '至少勾選' in warning.call_args.args[2]
d.type_actions['CSS'].setChecked(True)
scan(d)
assert len(d.rows) == 1 and d.rows[0]['name'] == 'OEBPS/style.css'
d.table.clicked.emit(d.proxy.mapFromSource(d.model.index(0,3)))
assert editors['OEBPS/style.css'].syntax == 'css'
d.single()
assert str(editors['OEBPS/style.css'].editor.toPlainText()) == 'p {color:blue}'
editors['OEBPS/style.css'].undo()
assert str(editors['OEBPS/style.css'].editor.toPlainText()) == 'p {color:red}'
d.set_types(False);d.type_actions['OPF'].setChecked(True)
d.pattern.setText('<itemref idref=');d.template.setText('<itemref linear="yes" idref=');scan(d)
assert d.rows and all(row['name'] == c.opf_name for row in d.rows)
d.table.clicked.emit(d.proxy.mapFromSource(d.model.index(0,3)))
assert editors[c.opf_name].syntax == 'xml'
assert editors[c.opf_name].editor.textCursor().selectedText() == '<itemref idref='
d.single()
assert 'linear="yes" idref=' in str(editors[c.opf_name].editor.toPlainText())
editors[c.opf_name].undo()
d.set_types(True)
js = edit_file('OEBPS/script.js', 'javascript')
js.replace_data('const color="green";')
d.pattern.setText('green');d.template.setText('purple');scan(d)
assert len(d.rows) == 1 and d.rows[0]['name'].endswith('.js')
d.select_row(0, 1);d.single()
assert str(js.editor.toPlainText()) == 'const color="purple";'
# XML/JSON integrity is checked on the complete result, not incomplete source snippets.
for source, pattern, template, syntax in [
    ('<package><itemref idref="x"/></package>', 'itemref', 'broken<', 'xml'),
    ('{"color":"red"}', 'red', '"', 'json'),
]:
    rows = search(source, pattern, template, syntax=syntax)
    try:
        replace(source, rows)
    except ValueError:
        pass
    else:
        raise AssertionError('invalid structured output accepted')
assert replace('a < b && b > 0', search('a < b && b > 0', 'b', 'c', syntax='javascript')) == 'a < c && c > 0'
d.close()
editors.clear()
print('PASS file types: checked defaults, filters, binary exclusion, OPF/CSS locate and write, unsaved JS, XML/JSON rejection')
