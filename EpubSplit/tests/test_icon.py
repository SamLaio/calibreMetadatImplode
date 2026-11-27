"""Run with calibre-debug -e in an isolated config directory."""
import importlib
from pathlib import Path
from types import SimpleNamespace
from zipfile import ZipFile
from calibre.gui2 import Application
from calibre.customize.zipplugin import loader
from qt.core import QAction

app = Application([])
package = Path(__file__).parents[2] / 'dist' / 'EpubSplit-zh_TW-release.zip'
base = loader.load(str(package))
module_name, class_name = base.actual_plugin.split(':')
action_class = getattr(importlib.import_module(module_name), class_name)

def resources(names):
    with ZipFile(package) as archive:
        return {name: archive.read(name) for name in names}

for version in (base.version, (1, 2), (1, 5, 0, 1, 0, 2)):
    declaration = SimpleNamespace(name=base.name, version=version)
    action = SimpleNamespace(name=base.name, interface_action_base_plugin=declaration,
                             load_resources=resources, qaction=QAction(), plugin_button=lambda: None)
    action_class.genesis(action)
    assert not action.qaction.icon().isNull(), 'EpubSplit icon is missing'
    assert action.version == base.name + ' v' + '.'.join(map(str, version))
print('PASS EpubSplit startup, full version and toolbar icon')
