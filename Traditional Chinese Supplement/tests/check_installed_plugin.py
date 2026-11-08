import importlib.util
import json
import os
import socket
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
from calibre.utils.config import config_dir
assert (ROOT / 'dist').resolve() in Path(config_dir).resolve().parents
from calibre.gui2 import Application
from qt.core import (QAbstractButton, QAction, QComboBox, QDoubleSpinBox, QFont,
                     QFontDatabase, QLineEdit, QMainWindow, QSpinBox, QWidget)
from calibre.customize.zipplugin import loader
from calibre.db.legacy import LibraryDatabase

app = Application([])
font_id = QFontDatabase.addApplicationFont('C:/Windows/Fonts/msjh.ttc')
families = QFontDatabase.applicationFontFamilies(font_id)
if families:
    app.setFont(QFont(families[0], 12))
name = sys.argv[-1]
archive = Path(os.environ['APPDATA']) / 'calibre/plugins' / (name + '.zip')
spec = importlib.util.spec_from_file_location('calibre_plugins.traditional_chinese_supplement',
    ROOT / 'Traditional Chinese Supplement/src/__init__.py',
    submodule_search_locations=[str(ROOT / 'Traditional Chinese Supplement/src')])
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
from calibre_plugins.traditional_chinese_supplement import ui, display

out = Path(config_dir).parent
out.mkdir(parents=True, exist_ok=True)
db = LibraryDatabase(str(ROOT / 'dist/tql' / out.name))
gui = QMainWindow()
gui.current_db = db
gui.must_restart_before_config = False
from calibre.gui2.ui import get_gui
get_gui.ans = gui
gui.keyboard = Mock()
gui.keyboard.shortcuts = {}
gui.iactions = {}
gui.library_view = Mock()
gui.library_view.model.return_value.db = db
gui.library_view.model.return_value.custom_columns = {}
gui.library_view.model.return_value.orig_headers = {'rating': '評分'}
gui.library_view.get_selected_ids.return_value = []

# No account access or network operations are part of UI translation tests.
def blocked(*args, **kwargs):
    raise AssertionError('Network access is forbidden in translation tests')
socket.socket.connect = blocked
socket.create_connection = blocked
plugin_class = loader.load(str(archive))
plugin = plugin_class(str(archive))
if hasattr(plugin, 'load_actual_plugin'):
    action = plugin.load_actual_plugin(gui)
    action.interface_action_base_plugin = plugin
    action.qaction = QAction(name, gui)
    plugin.actual_plugin_ = action
if name == 'DeDRM':
    plugin.alfdir = str(out / 'DeDRM')
    Path(plugin.alfdir).mkdir(exist_ok=True)
if name == 'Goodreads Sync':
    from calibre_plugins.goodreads_sync import config as cfg
    cfg.plugin_prefs[cfg.STORE_USERS] = {'QA': {cfg.KEY_USER_ID: '0', cfg.KEY_USER_TOKEN: '', cfg.KEY_USER_SECRET: '', cfg.KEY_SHELVES: []}}
with plugin:
    if name == 'DeACSM':
        plugin.initialize()
    if name in ('XTC Output', 'Markdown Output'):
        if name == 'XTC Output':
            from calibre_plugins.calibre_xtc_output.config import PluginWidget
        else:
            from calibre_plugins.markdown_output.ui import PluginWidget
        opts = {o.option.name: o for o in plugin.options}
        widget = PluginWidget(gui, lambda key: opts[key], lambda key: '', db=db)
    elif name == 'Chinese Text Conversion':
        from calibre_plugins.chinese_text.dialogs import ConversionDialog
        import inspect
        print('CONVERSION_SIGNATURE', inspect.signature(ConversionDialog))
        from calibre_plugins.chinese_text import main as conversion
        prefs = conversion.getPrefs()
        defaults = dict(input_source=0, conversion_type=0, input_locale=0, output_locale=0,
                        use_target_phrases=True, quotation_type=0, output_orientation=0,
                        update_punctuation=False, punc_omits=conversion.PUNC_OMITS)
        prefs.defaults.update(defaults)
        widget = ConversionDialog(gui, prefs, conversion._h2v_master_dict, conversion.PUNC_OMITS)
    else:
        widget = plugin.config_widget()
assert isinstance(widget, QWidget), repr(widget)
widget.setParent(gui)


def semantics():
    rows = []
    for child in widget.findChildren(QWidget):
        key = (id(child), child.objectName(), child.isEnabled())
        if isinstance(child, QComboBox):
            rows.append((key, child.currentIndex(), [(child.itemText(i), child.itemData(i)) for i in range(child.count())]))
        elif isinstance(child, QLineEdit):
            rows.append((key, child.text()))
        elif isinstance(child, QAbstractButton):
            rows.append((key, child.isChecked()))
        elif isinstance(child, (QSpinBox, QDoubleSpinBox)):
            rows.append((key, child.value()))
    return repr(rows)

def saved_settings():
    save = getattr(widget, 'save_settings', None)
    if not callable(save):
        save = getattr(widget, 'commit', None)
    if not callable(save):
        save = getattr(widget, 'savePrefs', None)
    if not callable(save):
        return None
    result = save()
    settings = {}
    for path in Path(config_dir).rglob('*.json'):
        try:
            settings[str(path.relative_to(config_dir))] = json.loads(path.read_text(encoding='utf-8'))
        except (ValueError, UnicodeError):
            pass
    return repr(result), settings

before_saved = saved_settings()
before = semantics()
print("BASELINE_READY", flush=True)
labels = [(c, c.text()) for c in widget.findChildren(QWidget) if hasattr(c, 'text') and not isinstance(c, QLineEdit)]
translator = ui.TranslationFilter(gui)
translator.start()
for child in [widget] + widget.findChildren(QWidget):
    translator.translate_safely(child)
assert semantics() == before, 'Translation changed a setting or identifier'
assert not translator.failures, str(translator.failures)
assert saved_settings() == before_saved, 'Saved configuration changed after translation'
widget.show()
gui.show()
app.processEvents()
assert semantics() == before, 'Show events changed a setting or identifier'
changed = [(old, c.text()) for c, old in labels if c.text() != old]
widget.grab().save(str(out / 'translated.png'))
result = {'plugin': name, 'widget_module': type(widget).__module__, 'scope': display.scope_for(widget),
          'changed_labels': len(changed), 'examples': changed[:5], 'semantics_preserved': True, 'save_roundtrip': before_saved is not None,
           'errors': list(translator.failures),
          'remaining_labels': sorted(set(c.text() for c in widget.findChildren(QWidget)
              if hasattr(c, 'text') and not isinstance(c, (QLineEdit, QComboBox))
              and isinstance(c.text(), str) and c.text().isascii() and len(c.text()) > 3))}
(out / 'result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(result, ensure_ascii=False))
translator.stop()
widget.close()
gui.close()
db.close()
