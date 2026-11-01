import importlib.util
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

sys.dont_write_bytecode = True
SOURCE = Path(__file__).resolve().parents[1] / 'src'
spec = importlib.util.spec_from_file_location('calibre_plugins.toolbar_manager', SOURCE / '__init__.py',
                                            submodule_search_locations=[str(SOURCE)])
plugin = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = plugin
spec.loader.exec_module(plugin)
from calibre_plugins.toolbar_manager import core, ui
from qt.core import (QAction, QApplication, QContextMenuEvent, QEvent, QMainWindow,
                     QMenu, QPoint, QToolBar, QToolButton, QHBoxLayout, QWidget, Qt)


class ToolbarManagerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.gui = QMainWindow()
        self.toolbars = [QToolBar(self.gui) for i in range(4)]
        for bar in self.toolbars:
            self.gui.addToolBar(bar)
        self.preferences = {
            'action-layout-toolbar': ('Preferences', 'Alpha', None, 'Beta'),
            'action-layout-toolbar-device': ('Location Manager', 'Alpha'),
            'action-layout-toolbar-child': ('Beta',),
            'action-layout-searchbar': ('Alpha',),
            'action-layout-menubar': (), 'action-layout-menubar-device': (),
        }
        self.prefs_patch = patch.object(ui, 'gprefs', self.preferences)
        self.prefs_patch.start()
        self.addCleanup(self.prefs_patch.stop)
        self.home_plugin = SimpleNamespace(name='Alpha', plugin_path='alpha.zip', homepage='https://example.com/alpha',
                                           is_customizable=lambda: True, do_user_config=Mock())
        self.gui.iactions = {}
        for name in ('Preferences', 'Alpha', 'Beta'):
            action = QAction(name, self.gui)
            self.gui.iactions[name] = SimpleNamespace(qaction=action, dont_remove_from=frozenset(),
                                                       interface_action_base_plugin=None)
        self.gui.iactions['Preferences'].do_config = Mock()
        self.gui.iactions['Alpha'].interface_action_base_plugin = self.home_plugin
        manager = SimpleNamespace(main_bars=tuple(self.toolbars[:2]), child_bars=(self.toolbars[2],),
                                  search_tool_bar=self.toolbars[3],
                                  location_manager=SimpleNamespace(all_actions=[]),
                                  menubar_fallback=(), menubar_device_fallback=())
        manager.init_bars = Mock(side_effect=self.rebuild)
        manager.update_bars = Mock()
        self.gui.bars_manager = manager
        self.action = ui.ToolbarManagerAction(self.gui, None)
        self.action.qaction = QAction('工具列管理', self.gui)
        self.action.interface_action_base_plugin = SimpleNamespace(
            load_resources=lambda names: {name: (SOURCE / name).read_bytes() for name in names})
        self.action.genesis()
        self.assertFalse(self.action.qaction.icon().isNull())
        self.rebuild()
        self.gui.resize(900, 200)
        self.gui.show()
        self.app.processEvents()
        self.addCleanup(self.action.shutting_down)
        self.addCleanup(self.gui.close)

    def rebuild(self):
        for bar, key in zip(self.toolbars, ('toolbar', 'toolbar-device', 'toolbar-child', 'searchbar')):
            bar.clear()
            for name in self.preferences['action-layout-' + key]:
                if name is None:
                    bar.addSeparator()
                elif name in self.gui.iactions:
                    bar.addAction(self.gui.iactions[name].qaction)

    def test_move_and_remove_persist_only_current_toolbar(self):
        original_device = self.preferences['action-layout-toolbar-device']
        self.action.edit_layout('toolbar', 'Alpha', 'right')
        self.assertEqual(self.preferences['action-layout-toolbar'], ('Preferences', None, 'Alpha', 'Beta'))
        self.action.edit_layout('toolbar', 'Alpha', 'left')
        self.action.edit_layout('toolbar', 'Alpha', 'remove')
        self.assertEqual(self.preferences['action-layout-toolbar'], ('Preferences', None, 'Beta'))
        self.assertEqual(self.preferences['action-layout-toolbar-device'], original_device)
        self.gui.bars_manager.update_bars.assert_called()

    def test_boundaries_and_stale_button_do_not_write(self):
        self.action.edit_layout('toolbar', 'Preferences', 'left')
        self.action.edit_layout('toolbar', 'missing', 'remove')
        self.gui.bars_manager.init_bars.assert_not_called()

    def test_last_preferences_and_location_are_protected(self):
        with patch.object(ui, 'error_dialog') as error:
            self.action.edit_layout('toolbar', 'Preferences', 'remove')
            self.action.edit_layout('toolbar-device', 'Location Manager', 'remove')
        self.assertEqual(error.call_count, 2)
        self.assertIn('Preferences', self.preferences['action-layout-toolbar'])
        self.assertIn('Location Manager', self.preferences['action-layout-toolbar-device'])

    def test_preferences_can_be_removed_when_menubar_has_entry(self):
        self.preferences['action-layout-menubar'] = ('Preferences',)
        self.action.edit_layout('toolbar', 'Preferences', 'remove')
        self.assertNotIn('Preferences', self.preferences['action-layout-toolbar'])

    def test_plugin_removal_restriction_is_respected(self):
        self.gui.iactions['Alpha'].dont_remove_from = frozenset(['toolbar'])
        with patch.object(ui, 'error_dialog') as error:
            self.action.edit_layout('toolbar', 'Alpha', 'remove')
        error.assert_called_once()
        self.assertIn('Alpha', self.preferences['action-layout-toolbar'])

    def test_failed_refresh_rolls_back_layout(self):
        original = self.preferences['action-layout-toolbar']
        self.gui.bars_manager.init_bars.side_effect = RuntimeError('refresh failed')
        with patch.object(ui, 'error_dialog'):
            self.action.edit_layout('toolbar', 'Alpha', 'remove')
        self.assertEqual(self.preferences['action-layout-toolbar'], original)

    def test_plugin_menu_order_and_configuration(self):
        menu, commands, original = self.action.make_menu('toolbar', 'Alpha', self.gui.iactions['Alpha'].qaction)
        self.assertEqual([a.text() for a in menu.actions() if not a.isSeparator()],
                         ['向左移動', '向右移動', '移除按鈕', '開啟插件首頁', '移除插件', '開啟選項', '開啟工具列選單'])
        option = next(a for a in menu.actions() if a.text() == '開啟選項')
        commands[option]()
        self.home_plugin.do_user_config.assert_called_once_with(parent=self.gui)
        menu.deleteLater()

    def test_builtin_menu_hides_plugin_commands(self):
        menu, _, _ = self.action.make_menu('toolbar', 'Preferences', self.gui.iactions['Preferences'].qaction)
        self.assertNotIn('移除插件', [a.text() for a in menu.actions()])
        self.assertNotIn('開啟插件首頁', [a.text() for a in menu.actions()])
        menu.deleteLater()

    def test_unknown_homepage_is_hidden_but_uninstall_is_available(self):
        self.home_plugin.homepage = 'javascript:bad()'
        menu, _, _ = self.action.make_menu('toolbar', 'Alpha', self.gui.iactions['Alpha'].qaction)
        self.assertNotIn('開啟插件首頁', [a.text() for a in menu.actions()])
        self.assertIn('移除插件', [a.text() for a in menu.actions()])
        menu.deleteLater()
        self.home_plugin.homepage = 'https://[bad'
        self.assertIsNone(core.homepage_for(self.home_plugin))

    def test_homepages_cover_project_plugins(self):
        for name in core.PROJECT_PLUGINS:
            self.assertTrue(core.homepage_for(SimpleNamespace(name=name, plugin_path='plugin.zip')).startswith('https://github.com/'))
        self.assertIsNone(core.homepage_for(SimpleNamespace(name='Alpha', plugin_path=None)))

    def test_search_layout_button_is_recognized(self):
        holder = QWidget(self.gui)
        layout = QHBoxLayout(holder)
        button = QToolButton(holder)
        button.setDefaultAction(self.gui.iactions['Alpha'].qaction)
        layout.addWidget(button)
        self.gui.bars_manager.search_tool_bar = layout
        self.action._active = True
        event = QContextMenuEvent(QContextMenuEvent.Reason.Keyboard, QPoint(), button.mapToGlobal(QPoint()))
        with patch.object(self.action, 'show_context_menu') as show:
            self.assertTrue(self.action.eventFilter(button, event))
            self.assertEqual(show.call_args.args[1], 'searchbar')
        self.assertIs(self.action.target_action(button, button, QPoint()), self.gui.iactions['Alpha'].qaction)

    def test_original_menu_retains_title_and_actions(self):
        action = self.gui.iactions['Alpha'].qaction
        original = QMenu('原始標題', self.gui)
        existing = original.addAction('原本功能')
        action.setMenu(original)
        original.setTitle('原始標題')
        with patch.object(self.action, 'target_action', return_value=action), \
                patch.object(ui.QMenu, 'exec', return_value=None):
            self.action.show_context_menu(self.toolbars[0], 'toolbar', self.toolbars[0], QPoint())
        self.assertEqual(original.title(), '原始標題')
        self.assertIn(existing, original.actions())
        self.assertIs(action.menu(), original)

    def test_context_event_finds_button_and_ignores_other_widgets(self):
        self.action._active = True
        button = self.toolbars[0].widgetForAction(self.gui.iactions['Alpha'].qaction)
        event = QContextMenuEvent(QContextMenuEvent.Reason.Mouse, QPoint(2, 2), button.mapToGlobal(QPoint(2, 2)))
        with patch.object(self.action, 'show_context_menu') as show:
            self.assertTrue(self.action.eventFilter(button, event))
            self.assertEqual(show.call_args.args[1], 'toolbar')
            self.assertFalse(self.action.eventFilter(self.gui, event))

    def test_event_filter_survives_toolbar_rebuild(self):
        self.action._active = True
        self.rebuild()
        button = self.toolbars[0].widgetForAction(self.gui.iactions['Alpha'].qaction)
        with patch.object(self.action, 'show_context_menu') as show:
            event = QContextMenuEvent(QContextMenuEvent.Reason.Keyboard, QPoint(), button.mapToGlobal(QPoint()))
            self.assertTrue(self.action.eventFilter(button, event))
            show.assert_called_once()

    def test_open_toolbar_settings_uses_native_preferences(self):
        self.action.open_toolbar_settings()
        self.gui.iactions['Preferences'].do_config.assert_called_once_with(
            initial_plugin=('Interface', 'Toolbar'), close_after_initial=True)

    def test_cancel_uninstall_never_removes_plugin(self):
        with patch.object(ui, 'question_dialog', return_value=False) as question, \
                patch.object(ui, 'uninstall_plugin') as remove:
            self.action.remove_plugin(self.home_plugin)
        remove.assert_not_called()
        self.assertFalse(question.call_args.kwargs['default_yes'])

    def test_confirmed_uninstall_disables_button_and_requires_restart(self):
        with patch.object(ui, 'question_dialog', return_value=True), \
                patch.object(ui, 'uninstall_plugin', return_value=True) as remove, \
                patch.object(ui, 'info_dialog') as info:
            self.action.remove_plugin(self.home_plugin)
        remove.assert_called_once_with(self.home_plugin)
        self.assertFalse(self.gui.iactions['Alpha'].qaction.isEnabled())
        self.assertIn('Alpha', self.action._removed_plugins)
        info.assert_called_once()
        self.assertIn('重新啟動', info.call_args.args[2])

    def test_failed_uninstall_does_not_disable_button(self):
        with patch.object(ui, 'question_dialog', return_value=True), \
                patch.object(ui, 'uninstall_plugin', return_value=False), \
                patch.object(ui, 'error_dialog') as error:
            self.action.remove_plugin(self.home_plugin)
        self.assertTrue(self.gui.iactions['Alpha'].qaction.isEnabled())
        self.assertNotIn('Alpha', self.action._removed_plugins)
        error.assert_called_once()

    def test_builtin_and_already_removed_plugin_cannot_be_uninstalled(self):
        self.action._removed_plugins.add('Alpha')
        with patch.object(ui, 'uninstall_plugin') as remove, patch.object(ui, 'question_dialog') as question:
            self.action.remove_plugin(self.home_plugin)
            self.action.remove_plugin(SimpleNamespace(name='builtin', plugin_path=None))
        remove.assert_not_called()
        question.assert_not_called()


if __name__ == '__main__':
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(ToolbarManagerTests))
    raise SystemExit(not result.wasSuccessful())
