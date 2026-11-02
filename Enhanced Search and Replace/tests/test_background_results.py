from time import monotonic, sleep
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from test_support import scan
from calibre.gui2 import Application
from calibre.gui2.tweak_book import editors, set_current_container
from calibre.gui2.tweak_book.boss import Boss
from calibre.gui2.tweak_book.editor.widget import Editor
from calibre.ebooks.oeb.polish.container import get_container
from calibre.customize.ui import all_edit_book_tool_plugins
from calibre.gui2.tweak_book.plugin import load_plugin_tools
from qt.core import QWidget, QTimer, Qt

app = Application([])
root = Path(__file__).resolve().parents[2]
c = get_container(str(root/'dist/text-regex-p0-fixture.epub'))
c.add_file('OEBPS/large.txt', ('targetvalue\n' * 30000).encode(), media_type='text/plain')
set_current_container(c)
plugin = next(p for p in all_edit_book_tool_plugins() if p.name == 'Enhanced Search and Replace')
list(load_plugin_tools(plugin))
from calibre_plugins.text_regex_p0.main import SearchDialog

gui = QWidget()
boss = SimpleNamespace()
boss.commit_editor_to_container = lambda name: Boss.commit_editor_to_container(boss, name)
boss.commit_all_editors_to_container = lambda: Boss.commit_all_editors_to_container(boss)


def edit_file(name, syntax='html'):
    if name not in editors:
        ed = editors[name] = Editor(syntax)
        ed.data = c.raw_data(name)
    return editors[name]


boss.edit_file = edit_file
d = SearchDialog(SimpleNamespace(gui=gui, boss=boss, current_container=c))
d.show()
d.pattern.setText('class="n"');d.template.setText('class="changed"')
scan(d)
assert not d.rows  # Text mode excludes attributes.
d.search_mode.setCurrentIndex(1)
scan(d)
assert len(d.rows) == 1 and d.rows[0]['raw_source']
d.select_row(0);d.single()
assert '<span class="changed">34</span>' in str(editors['OEBPS/chapter.xhtml'].editor.toPlainText())
editors['OEBPS/chapter.xhtml'].undo()
d.set_types(False);d.type_actions['TXT'].setChecked(True)
d.pattern.setText('targetvalue');d.template.setText('changed')
ticks, values = [], []
heartbeat = QTimer()
heartbeat.setInterval(5)
heartbeat.timeout.connect(lambda: (ticks.append(monotonic()), values.append(d.progress.value())))
heartbeat.start()
large_html = '<html><body><p>' + '這是長篇測試。' * 100000 + '結束標記</p></body></html>'
c.add_file('OEBPS/large.xhtml', large_html.encode('utf-8'), media_type='application/xhtml+xml')
d.set_types(False);d.type_actions['XHTML'].setChecked(True)
d.search_mode.setCurrentIndex(0)
d.pattern.setText('結束標記')
scan(d)
assert len(d.rows) == 1 and ticks
print(f'PASS large HTML projection: {len(large_html.encode("utf-8")) / 1048576:.1f} MiB, {len(ticks)} UI timer ticks')
ticks.clear()
d.set_types(False);d.type_actions['TXT'].setChecked(True)
d.pattern.setText('targetvalue')
started = monotonic()
d.scan()
assert monotonic() - started < 0.5 and d.busy
deadline = monotonic() + 30
while d.busy:
    app.processEvents();sleep(0.001)
    assert monotonic() < deadline
assert len(d.rows) == 30000 and ticks and d.progress.value() == 1000
assert d.model.rowCount() == 30000
print(f'PASS responsive search: 30,000 hits, {len(ticks)} UI timer ticks, {monotonic() - started:.2f}s')
d.scan()
QTimer.singleShot(20, d.cancel_search)
deadline = monotonic() + 10
while d.busy:
    app.processEvents();sleep(0.001)
    assert monotonic() < deadline
assert '取消' in d.status.text() and d.worker is None
heartbeat.stop()
# Change the source only after the worker has stopped.
with c.open('OEBPS/large.txt', 'wb') as stream:
    stream.write(b'target10 target2 target100')
d.pattern.setText(r'target\d+');scan(d)
d.header_clicked(3);d.header_clicked(3)
assert [d.proxy.index(i,3).data() for i in range(3)] == ['17', '9', '0']
order = d.visible_rows()
d.corner_button.click()
assert all(row.get('checked') for row in d.rows)
assert d.visible_rows() == order and d.proxy.sortColumn() == 3
assert not d.table.selectionModel().selectedIndexes()
d.corner_button.click()
assert not any(row.get('checked') for row in d.rows)
d.table.horizontalHeader().sectionClicked.emit(0)
assert d.visible_rows() == order and not any(row.get('checked') for row in d.rows)
assert d.table.horizontalHeader().sortIndicatorSection() == 3

d.table.setCurrentIndex(d.proxy.index(0,1))
d.table.clicked.emit(d.proxy.index(0,3))
assert editors['OEBPS/large.txt'].editor.textCursor().selectedText() == 'target100'
d.single()
assert str(editors['OEBPS/large.txt'].editor.toPlainText()) == 'target10 target2 changed'
assert d.current_row() == 1  # Continue in the displayed descending order.
d.filter.setCurrentIndex(1)
assert d.proxy.rowCount() == 2
d.corner_button.click()
assert d.rows[0]['checked'] and d.rows[1]['checked'] and not d.rows[2].get('checked')
d.batch()
assert str(editors['OEBPS/large.txt'].editor.toPlainText()) == 'changed changed changed'
assert d.proxy.rowCount() == 0
d.filter.setCurrentIndex(2)
assert d.proxy.rowCount() == 3
assert all(row['done'] for row in d.rows)
d.filter.setCurrentIndex(0);scan(d)  # Current source has no original hits.
assert not d.rows
d.pattern.setText('changed');d.template.setText(r'\g<missing>');scan(d)
d.filter.setCurrentIndex(3)
assert d.proxy.rowCount() == 3
d.template.setText('fixed')
assert d.proxy.rowCount() == 0
d.filter.setCurrentIndex(1)
assert d.proxy.rowCount() == 3
# Closing a running worker requests cancellation and waits for it.
c.add_file('OEBPS/closing.txt', b'fixed\n' * 300000, media_type='text/plain')
d.pattern.setText('fixed');d.scan()
deadline = monotonic() + 10
while d.worker is None:
    app.processEvents();sleep(0.001)
    assert monotonic() < deadline
assert d.worker.isRunning()
d.close()
deadline = monotonic() + 10
while d.busy:
    app.processEvents();sleep(0.001)
    assert monotonic() < deadline
assert d.worker is None
editors.clear()
print('PASS raw HTML, progress/cancel/close, numeric sorting, filtered selection/replacement, status filters')
