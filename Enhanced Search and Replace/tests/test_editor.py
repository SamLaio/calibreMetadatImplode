from pathlib import Path
from unittest.mock import patch
import sys
from calibre.gui2 import Application
app=Application([])
p=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(p/'src'))
from core import search,replace,utf16
from calibre.gui2.tweak_book.editor.widget import Editor
from calibre.gui2.tweak_book import editors
from qt.core import QTextCursor
ed=Editor('html');editors['OEBPS/chapter.xhtml']=ed
raw=(p/'fixtures/chapter.xhtml').read_text(encoding='utf-8')
ed.data=raw
raw=str(ed.editor.toPlainText())
rows=search(raw,r'第(\d+)章','第$1回')
changed=replace(raw,[rows[0]])
ed.replace_data(changed)
assert str(ed.editor.toPlainText())==changed
ed.undo();assert str(ed.editor.toPlainText())==raw
ed.redo();assert str(ed.editor.toPlainText())==changed
c=ed.editor.textCursor();start=changed.index('第12回');c.setPosition(utf16(changed,start));c.setPosition(utf16(changed,start+4),QTextCursor.MoveMode.KeepAnchor)
assert c.selectedText()=='第12回'
print('PASS Calibre 9.17 real Editor: replace_data, Undo, Redo, UTF16 selection')
# Exercise the real container commit method with a minimal Boss receiver.
from types import SimpleNamespace
from calibre.ebooks.oeb.polish.container import get_container
from calibre.gui2.tweak_book import set_current_container
from calibre.gui2.tweak_book.boss import Boss
container=get_container(str(p.parent/'dist/text-regex-p0-fixture.epub'))
set_current_container(container)
boss=SimpleNamespace()
boss.commit_editor_to_container=lambda name: Boss.commit_editor_to_container(boss,name)
ed.is_synced_to_container=False
assert Boss.commit_all_editors_to_container(boss)
assert container.raw_data('OEBPS/chapter.xhtml') == changed
assert ed.is_synced_to_container
print('PASS real Boss commit_all_editors_to_container, temporary container only')


from calibre.customize.ui import all_edit_book_tool_plugins
from calibre.gui2.tweak_book.plugin import load_plugin_tools
plugin=next(p for p in all_edit_book_tool_plugins() if p.name=='Enhanced Search and Replace')
tools=list(load_plugin_tools(plugin))
assert len(tools)==1
from calibre_plugins.text_regex_p0.main import SearchDialog
from qt.core import QWidget, Qt, QHeaderView
# Real dialog/widgets and real Editor, minimal host instead of full Main/WebEngine.
gui=QWidget();gui.central=SimpleNamespace(current_editor=ed)
action_host=SimpleNamespace(gui=gui,open_dialog=lambda: None)
for for_toolbar in (True, False):
    action=type(tools[0]).create_action(action_host,for_toolbar=for_toolbar)
    assert action.text()=='Enhanced Search and Replace'
    assert not action.icon().pixmap(32,32).isNull()
assert tools[0].allowed_in_toolbar and tools[0].allowed_in_menu
boss.commit_all_editors_to_container=lambda: Boss.commit_all_editors_to_container(boss)
boss.show_editor=lambda name: None
boss.edit_file=lambda name, syntax='html': editors[name]
tool=SimpleNamespace(gui=gui,boss=boss,current_container=container)
d=SearchDialog(tool)
assert d.pattern.text()=='' and d.template.text()==''
header=d.table.horizontalHeader()
assert all(header.sectionResizeMode(i)==QHeaderView.ResizeMode.Interactive for i in range(6))
header.resizeSection(1,180)
header.sectionClicked.emit(0)  # Empty results are harmless.
d.pattern.setText(r'第(\d+)章');d.template.setText('第$1回')
d.show();app.processEvents();d.scan()
assert len(d.rows)==4
assert d.rows[1]['safe'] is True
assert header.sectionsClickable()
header.sectionClicked.emit(0)
assert all(d.table.item(i,0).checkState()==Qt.CheckState.Checked for i in range(len(d.rows)))
header.sectionClicked.emit(1)
assert d.table.item(0,0).checkState()==Qt.CheckState.Checked
header.sectionClicked.emit(0)
assert all(d.table.item(i,0).checkState()==Qt.CheckState.Unchecked for i in range(len(d.rows)))
d.table.item(0,0).setCheckState(Qt.CheckState.Checked)
header.sectionClicked.emit(0)  # Partial selection becomes all checked.
assert all(d.table.item(i,0).checkState()==Qt.CheckState.Checked for i in range(len(d.rows)))
header.sectionClicked.emit(0)
# Replacement edits refresh cached matches without clearing rows or rerunning search.
saved_rows=d.rows
d.table.item(0,0).setCheckState(Qt.CheckState.Checked)
d.table.setCurrentCell(0,1)
with patch('calibre_plugins.text_regex_p0.main.search', side_effect=AssertionError('unexpected search')):
    with patch('calibre_plugins.text_regex_p0.main.QMessageBox.warning') as warning:
        for template, after in [('第$1節','第3節'), (r'第\g<1>回','第3回'), ('','')]:
            d.template.setText(template)
            assert d.rows is saved_rows and d.rows[0]['after']==after
            assert d.table.item(0,2).text()==after
            assert d.table.item(0,0).checkState()==Qt.CheckState.Checked
            assert d.table.currentRow()==0 and header.sectionSize(1)==180
        d.template.setText(r'\g<missing>')
        assert d.rows[0]['error'] and not d.rows[0]['safe']
        d.template.setText('第$1節')
        assert d.rows[0]['safe'] and not d.rows[0]['error']
        assert d.rows[1]['safe']  # Preserved groups keep their inline formatting.
        warning.assert_not_called()
assert str(ed.editor.toPlainText())==changed
# Apply the freshly edited preview without an intervening search.
d.single()
assert '第3節' in str(ed.editor.toPlainText())
ed.undo();assert str(ed.editor.toPlainText())==changed
# Changing the search pattern still invalidates old results.
d.pattern.setText(r'第([0-9]+)章')
assert not d.rows and d.table.rowCount()==0
d.scan()
assert d.rows[0]['after']=='第3節'
d.template.setText('第$1回');d.scan()
d.template.setText(r'\g<missing>')
with patch('calibre_plugins.text_regex_p0.main.QMessageBox.warning') as warning:
    d.guard(d.scan)
    warning.assert_not_called()
assert d.rows and d.table.rowCount() == len(d.rows)
assert '取代式無效' in d.table.item(0,4).text()
d.table.setCurrentCell(0,1);d.locate()
assert ed.editor.textCursor().selectedText()=='第3章'
with patch('calibre_plugins.text_regex_p0.main.QMessageBox.warning') as warning:
    d.guard(d.single)
    assert '取代失敗' in warning.call_args.args[2]
    d.guard(d.single)
    assert warning.call_count==1
    d.template.setText('第$1回');d.template.setText(r'\g<missing>')
    d.guard(d.single)
    assert warning.call_count==1
    d.guard(d.scan)
    assert warning.call_count==1
    d.table.setCurrentCell(0,1);d.guard(d.single)
    assert warning.call_count==2
assert str(ed.editor.toPlainText()) == changed
d.template.setText('第$1回');d.scan()
# Ambiguous replacement across different formats must reject before editing.
d.template.setText('新內容')
before=str(ed.editor.toPlainText())
try: d.apply([d.rows[1]])
except ValueError: pass
else: raise AssertionError('unsafe write accepted')
assert str(ed.editor.toPlainText())==before
# Failure dialog identifies the file/rows; the list and check states survive.
saved_rows=d.rows
d.table.item(0,0).setCheckState(Qt.CheckState.Checked)
d.table.item(1,0).setCheckState(Qt.CheckState.Checked)
with patch('calibre_plugins.text_regex_p0.main.QMessageBox.warning') as warning:
    d.guard(d.batch)
    message=warning.call_args.args[2]
    assert 'OEBPS/chapter.xhtml' in message and '第 2 筆' in message
    assert '尚未寫入內容' in message
assert d.rows is saved_rows and d.table.rowCount()==len(saved_rows)
assert d.table.item(1,0).checkState()==Qt.CheckState.Checked
assert '取代失敗' in d.table.item(1,4).text()
assert str(ed.editor.toPlainText())==before
d.table.item(1,0).setCheckState(Qt.CheckState.Unchecked)
d.template.setText('第$1回')
# A sync error must not claim that nothing changed or discard the old results.
with patch.object(boss, 'commit_all_editors_to_container', side_effect=RuntimeError('同步測試失敗')):
    with patch('calibre_plugins.text_regex_p0.main.QMessageBox.warning') as warning:
        d.guard(d.batch)
        message=warning.call_args.args[2]
        assert '同步書籍內容' in message and '可能已變更' in message
assert d.rows is saved_rows and '取代失敗' in d.table.item(0,4).text()
ed.undo();assert str(ed.editor.toPlainText())==before
d.scan()
# Real table check state drives batch; one safe row remains selected.
d.table.item(0,0).setCheckState(Qt.CheckState.Checked)
d.batch()
assert '第3回' in str(ed.editor.toPlainText())
ed.undo();assert str(ed.editor.toPlainText())==before
ed.redo();assert '第3回' in str(ed.editor.toPlainText())
# Undo makes the previously searched snapshot stale.
ed.undo()
try: d.fresh()
except ValueError: pass
else: raise AssertionError('stale results accepted')
d.scan();d.table.setCurrentCell(0,1);d.locate()
assert ed.editor.textCursor().selectedText()=='第3章'
d.single()
assert '第3回' in str(ed.editor.toPlainText())
assert header.sectionSize(1)==180
ed.replace_data('<html><body><p>第1章 第22章 第333章</p></body></html>')
d.scan();d.table.setCurrentCell(0,1)
d.single()
assert d.rows[d.table.currentRow()]['before']=='第22章'
d.template.setText('第$1章')
d.single()
assert d.rows[d.table.currentRow()]['before']=='第333章'
d.template.setText('第$1回')
d.single()
assert d.table.currentRow()==-1
assert len(d.rows)==3 and d.rows[1]['before']=='第22章'
assert len(d.rows)==3 and all(row['done'] for row in d.rows) and d.table.currentRow()==-1
assert all(d.table.item(i,4).text()=='已取代' for i in range(3))
saved_after=[row['after'] for row in d.rows]
d.template.setText('其他取代文字')
assert [row['after'] for row in d.rows]==saved_after
header.sectionClicked.emit(0)
assert all(d.table.item(i,0).checkState()==Qt.CheckState.Unchecked for i in range(3))
d.table.setCurrentCell(0,1)
d.locate()
assert ed.editor.textCursor().selectedText()=='第1回'
before_repeat=str(ed.editor.toPlainText())
with patch('calibre_plugins.text_regex_p0.main.QMessageBox.warning') as warning:
    d.guard(d.single)
    assert '已取代' in warning.call_args.args[2]
assert str(ed.editor.toPlainText())==before_repeat and d.table.item(0,4).text()=='已取代'
ed.replace_data('<html><body><p>第1章 第22章 第333章</p></body></html>')
d.template.setText('長<&$1');d.scan();d.table.setCurrentCell(1,1)
d.single()
assert d.rows[d.table.currentRow()]['before']=='第333章'
d.table.setCurrentCell(0,1);d.single()
d.table.setCurrentCell(1,1);d.locate()
assert ed.editor.textCursor().selectedText()=='長&lt;&amp;22'
d.table.setCurrentCell(2,1);d.single()
assert str(ed.editor.toPlainText())=='<html><body><p>長&lt;&amp;1 長&lt;&amp;22 長&lt;&amp;333</p></body></html>'
assert all(row['done'] for row in d.rows)
source='<html><body><p>第<span class="tcy">10</span>話</p><p>第20話</p></body></html>'
ed.replace_data(source)
d.pattern.setText(r'第(\d+)話');d.template.setText('第$1章');d.scan()
assert d.mode.currentData()=='text'
d.table.setCurrentCell(0,1);d.single()
assert str(ed.editor.toPlainText())==source.replace('10</span>話','10</span>章')
assert d.rows[0]['done'] and d.table.currentRow()==1
d.table.cellClicked.emit(1,3)
assert ed.editor.textCursor().selectedText()=='第20話'
d.table.cellClicked.emit(0,3)
assert ed.editor.textCursor().selectedText()=='第<span class="tcy">10</span>章'
d.table.setCurrentCell(1,1)
retained=d.rows
with patch('calibre_plugins.text_regex_p0.main.search', side_effect=AssertionError('mode switch must not search')):
    with patch('calibre_plugins.text_regex_p0.main.QMessageBox.warning') as warning:
        d.mode.setCurrentIndex(1)
        d.template.setText('<b>第$1章')
        assert not d.rows[1]['safe'] and 'XHTML' in d.table.item(1,4).text()
        d.template.setText('<b>第$1章</b>')
        assert d.rows[1]['safe']
        assert d.rows is retained and d.rows[0]['after']=='第10章'
        warning.assert_not_called()
d.single()
assert str(ed.editor.toPlainText())==source.replace('10</span>話','10</span>章').replace('第20話','<b>第20章</b>')
assert all(row['done'] for row in d.rows)
ed.undo()
assert str(ed.editor.toPlainText())==source.replace('10</span>話','10</span>章')
with patch('calibre_plugins.text_regex_p0.main.QMessageBox.warning') as warning:
    d.table.cellClicked.emit(1,3)
    assert '內容已變更' in warning.call_args.args[2]
ed.replace_data('<html><body>刪除我</body></html>')
d.pattern.setText('刪除我');d.template.setText('');d.mode.setCurrentIndex(0);d.scan()
d.table.setCurrentCell(0,1);d.single()
d.table.cellClicked.emit(0,3)
assert ed.editor.textCursor().position()==len('<html><body>')
assert ed.editor.textCursor().selectedText()==''
d.close()
print('PASS installed ZIP tool discovery; real dialog scan, checked batch, single, locate, stale/unsafe rejection')
