"""Launch the packaged plugin in an isolated calibre main window."""
import json
import traceback
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
for index in range(60):
    mi = Metadata('測試書籍 ' + str(index), ['作者' + str(index % 6)])
    mi.tags = ['歷史', '台灣'] if index % 3 else ['科幻', '推理', '文學']
    mi.series = '測試系列 ' + str(index % 4)
    db.create_book_entry(mi)
db.close()
prefs['library_path'] = str(library)
prefs['language'] = 'zh_TW'
from calibre.customize.ui import add_plugin
add_plugin(str(root / 'dist' / 'TagCloud.zip'))
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
        action = gui.iactions['Tag Cloud']
        panel = action.panel
        assert action.qaction.isEnabled() and panel.isVisible()
        assert action.splitter.widget(0) is gui.tags_view
        assert dict(panel.counts)['歷史'] == 40
        panel.clicked(QUrl('tag:' + str(panel.names.index('歷史'))))
        assert len(gui.current_db.new_api.search(gui.search.currentText())) == 40
        panel.field.setCurrentIndex(panel.field.findData('authors'))
        assert len(panel.counts) == 6
        panel.field.setCurrentIndex(panel.field.findData('tags'))
        gui.resize(1400, 900)
        action.splitter.setSizes([450, 320])
        app.processEvents()
        gui.grab().save(str(root / 'dist' / 'tag-cloud-native.png'))
        result = {'success': True, 'checks': ['package load', 'sidebar', 'tag search', 'authors', 'render']}
    except Exception:
        result = {'success': False, 'error': traceback.format_exc()}
    (profile / 'result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    gui.quit()


QTimer.singleShot(6500, verify)
run_gui_(opts, args, app)
