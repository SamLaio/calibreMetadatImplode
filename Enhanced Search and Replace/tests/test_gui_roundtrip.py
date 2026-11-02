"""Run edit and reopen phases in separate, isolated real Edit Book processes."""
import os
import sys
import time
import traceback
from pathlib import Path
from zipfile import ZipFile

if os.environ.get('ESR_GUI_PHASE') == 'prepare':
    from calibre.ebooks.oeb.polish.container import get_container
    c = get_container(str(Path(__file__).resolve().parents[2]/'dist/text-regex-p0-fixture.epub'))
    c.add_file('OEBPS/second.xhtml', '<html xmlns="http://www.w3.org/1999/xhtml"><body><p>第99章</p></body></html>'.encode('utf-8'),
               media_type='application/xhtml+xml', spine_index=1)
    c.commit(os.environ['ESR_GUI_BOOK'])
    sys.exit(0)

from calibre.utils.webengine import setup_fake_protocol, setup_default_profile
setup_fake_protocol()
import calibre.customize.ui
from calibre.gui2 import Application, set_gui_prefs
from calibre.gui2.tweak_book import tprefs, current_container, editors
from calibre.gui2.tweak_book.main import option_parser
from qt.core import QTimer, sip

set_gui_prefs(tprefs)
app = Application(['ebook-edit'], color_prefs=tprefs)
app.setQuitOnLastWindowClosed(False)
setup_default_profile()
app.load_builtin_fonts()
from calibre.gui2.tweak_book.ui import Main
from calibre.gui2.tweak_book.plugin import _tool_memory

opts, args = option_parser().parse_args(['ebook-edit'])
gui = Main(opts)
gui.show()
book = Path(os.environ['ESR_GUI_BOOK']).resolve()
phase = os.environ.get('ESR_GUI_PHASE', 'edit')
gui.boss.open_book(str(book))
state = {'step': 'open', 'deadline': time.monotonic() + 90, 'preview': ''}
dialog = None
exit_code = 1


def finish(success):
    global exit_code
    exit_code = 0 if success else 1
    timer.stop()
    if dialog is not None:
        dialog.close()
    # Failures only discard this generated test copy; never a user book.
    if not success:
        gui.action_save.setEnabled(False)
    gui.close()  # Real Boss.quit/shutdown and native save-manager cleanup.


def poll():
    global dialog
    try:
        assert time.monotonic() < state['deadline'], f"GUI timeout: {state['step']}"
        step = state['step']
        if step == 'open':
            c = current_container()
            if c is None or not hasattr(gui.boss, 'global_undo') or gui.boss.global_undo.pos < 1:
                return
            assert Path(c.path_to_ebook) == book
            tool = next(t for t in _tool_memory if t.plugin.name == 'Enhanced Search and Replace')
            assert not tool.create_action(True).icon().isNull()
            tool.open_dialog()
            dialog = tool.dialog
            dialog.pattern.setText(r'第(\d+)章')
            dialog.template.setText('第$1回')
            dialog.action_buttons[0].click()
            state['step'] = 'searched'
        elif step == 'searched' and not dialog.busy:
            if phase == 'reopen':
                assert not dialog.rows
                raw = current_container().raw_data('OEBPS/chapter.xhtml')
                assert '第12回' in raw and 'class="roundtrip"' in raw
                assert '34</span>回' in raw
                assert '第99回' in current_container().raw_data('OEBPS/second.xhtml')
                gui.boss.edit_file('OEBPS/chapter.xhtml', syntax='html')
                state['step'] = 'preview'
            else:
                assert len(dialog.rows) == 6
                dialog.select_row(0)
                dialog.action_buttons[2].click()
                ed = editors['OEBPS/chapter.xhtml']
                assert '第12回' in str(ed.editor.toPlainText())
                gui.boss.do_editor_undo()
                assert '第12章' in str(ed.editor.toPlainText())
                gui.boss.do_editor_redo()
                assert '第12回' in str(ed.editor.toPlainText())
                dialog.search_mode.setCurrentIndex(1)
                dialog.pattern.setText('class="n"')
                dialog.template.setText('class="roundtrip"')
                dialog.action_buttons[0].click()
                state['step'] = 'raw'
        elif step == 'raw' and not dialog.busy:
            assert len(dialog.rows) == 1
            dialog.select_row(0)
            dialog.action_buttons[2].click()
            dialog.search_mode.setCurrentIndex(0)
            dialog.pattern.setText(r'第(\d+)章')
            dialog.template.setText('第$1回')
            dialog.action_buttons[0].click()
            state['step'] = 'batch'
        elif step == 'batch' and not dialog.busy:
            assert len(dialog.rows) == 5
            dialog.toggle_checks(0)
            dialog.action_buttons[3].click()
            assert all(row.get('done') for row in dialog.rows)
            assert gui.action_save.isEnabled()
            gui.action_save.trigger()
            state['step'] = 'saved'
        elif step == 'saved' and not gui.boss.save_manager.has_tasks:
            assert not gui.action_save.isEnabled()
            with ZipFile(book) as archive:
                raw = archive.read('OEBPS/chapter.xhtml').decode('utf-8')
                assert '第12回' in raw and 'class="roundtrip"' in raw
                assert '34</span>回' in raw and '56</b><i>回</i>' in raw
                assert '第99回' in archive.read('OEBPS/second.xhtml').decode('utf-8')
            gui.boss.edit_file('OEBPS/chapter.xhtml', syntax='html')
            state['step'] = 'preview'
        elif step == 'preview':
            gui.preview.view.page().toPlainText(lambda text: state.update(preview=text))
            if '第12回' not in state['preview'] or '第34回' not in state['preview']:
                return
            assert not gui.action_save.isEnabled()
            print(f'PASS real GUI {phase}: native window/tool/buttons, preview, disk contents and clean close', flush=True)
            finish(True)
    except Exception:
        traceback.print_exc()
        finish(False)


timer = QTimer()
timer.setInterval(50)
timer.timeout.connect(poll)
timer.start()
app.exec()
from calibre.gui2.tweak_book.preview import parse_worker
deadline = time.monotonic() + 15
while parse_worker.is_alive() and time.monotonic() < deadline:
    time.sleep(0.05)
from calibre.ebooks.oeb.polish.check.css import shutdown
shutdown()
sip.delete(gui)
sys.exit(exit_code)
