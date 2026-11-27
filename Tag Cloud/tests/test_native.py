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
for index in range(60):
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
        gui.resize(1400, 900)
        action.splitter.setSizes([450, 320])
        app.processEvents()
        gui.grab().save(str(root / 'dist' / 'tag-cloud-native.png'))
        result = {'success': True, 'checks': ['package load', 'four visibility states', 'bottom button', 'cloud-only resize', 'all words', 'tag search', 'authors', 'render']}
        result['packages'] = len(packages)
        result['interface_actions'] = expected_actions
    except Exception:
        result = {'success': False, 'error': traceback.format_exc()}
    (profile / 'result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    gui.quit()


QTimer.singleShot(6500, verify)
run_gui_(opts, args, app)
