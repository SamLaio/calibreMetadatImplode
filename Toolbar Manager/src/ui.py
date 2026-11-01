from functools import partial
from html import escape

from qt.core import QApplication, QEvent, QIcon, QMenu, QPixmap, QTimer, QToolButton, QUrl, QWidget, Qt
from calibre.gui2 import error_dialog, gprefs, info_dialog, open_url, question_dialog
from calibre.customize.ui import remove_plugin as uninstall_plugin
from calibre.gui2.actions import InterfaceAction
from calibre_plugins.toolbar_manager.core import change_layout, homepage_for, validate_removal


class ToolbarManagerAction(InterfaceAction):
    name = 'Toolbar Manager'
    action_spec = ('工具列管理', None, '右鍵管理工具列；點選開啟工具列與選單設定', None)
    action_type = 'global'

    def genesis(self):
        pixmap = QPixmap()
        pixmap.loadFromData(self.interface_action_base_plugin.load_resources(
            ['images/toolbar-manager.svg'])['images/toolbar-manager.svg'])
        self.qaction.setIcon(QIcon(pixmap))
        self.qaction.triggered.connect(self.open_toolbar_settings)
        self._active = False
        self._removed_plugins = set()
        self._suppress_mouse_context = False

    def initialization_complete(self):
        self._active = True
        QApplication.instance().installEventFilter(self)

    def shutting_down(self):
        self._active = False
        app = QApplication.instance()
        if app is not None:
            app.removeEventFilter(self)
        return True

    def toolbar_locations(self):
        manager = self.gui.bars_manager
        locations = [(manager.main_bars[0], 'toolbar'),
                (manager.main_bars[1], 'toolbar-device'),
                (manager.child_bars[0], 'toolbar-child'),
                ]
        search = manager.search_tool_bar
        if isinstance(search, QWidget):
            locations.append((search, 'searchbar'))
        else:
            for index in range(search.count()):
                widget = search.itemAt(index).widget()
                if isinstance(widget, QToolButton):
                    locations.append((widget, 'searchbar'))
        return locations

    def eventFilter(self, watched, event):
        if not self._active or not isinstance(watched, QWidget):
            return False
        kind = event.type()
        mouse = kind == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.RightButton
        context = kind == QEvent.Type.ContextMenu
        if not (mouse or context):
            return False
        locations = dict(self.toolbar_locations())
        node = watched
        while node is not None and node not in locations:
            node = node.parentWidget()
        if node is None:
            return False
        if context and self._suppress_mouse_context and event.reason() == event.Reason.Mouse:
            self._suppress_mouse_context = False
            return True
        if mouse:
            self._suppress_mouse_context = True
        position = event.globalPosition().toPoint() if mouse else event.globalPos()
        self.show_context_menu(node, locations[node], watched, position)
        return True

    def target_action(self, bar, watched, position):
        if hasattr(bar, 'actionAt'):
            return bar.actionAt(bar.mapFromGlobal(position))
        node = watched
        while node is not None:
            if isinstance(node, QToolButton):
                return node.defaultAction()
            node = node.parentWidget()
        return None

    def action_name(self, bar, action, watched):
        for name, candidate in self.gui.iactions.items():
            if candidate.qaction is action and action is not None:
                return name
        if action in self.gui.bars_manager.location_manager.all_actions:
            return 'Location Manager'
        button = getattr(bar, 'donate_button', None)
        if button is not None and (watched is button or button.isAncestorOf(watched)):
            return 'Donate'
        return None

    def make_menu(self, key, name, action):
        menu = QMenu(self.gui)
        commands = {}
        layout = tuple(gprefs['action-layout-' + key])
        if name is not None and name in layout:
            index = layout.index(name)
            for label, operation, allowed in (
                    ('向左移動', 'left', index > 0),
                    ('向右移動', 'right', index < len(layout) - 1),
                    ('移除按鈕', 'remove', True)):
                item = menu.addAction(label)
                item.setEnabled(allowed)
                commands[item] = partial(self.edit_layout, key, name, operation)
            menu.addSeparator()
            candidate = self.gui.iactions.get(name)
            plugin = getattr(candidate, 'interface_action_base_plugin', None)
            if plugin is not None and plugin.name in self._removed_plugins:
                plugin = None
            homepage = homepage_for(plugin)
            if homepage:
                commands[menu.addAction('開啟插件首頁')] = partial(open_url, QUrl(homepage))
            if plugin is not None and getattr(plugin, 'plugin_path', None):
                commands[menu.addAction('移除插件')] = partial(self.remove_plugin, plugin)
                if plugin.is_customizable():
                    commands[menu.addAction('開啟選項')] = partial(plugin.do_user_config, parent=self.gui)
        commands[menu.addAction('開啟工具列選單')] = self.open_toolbar_settings
        original = action.menu() if action is not None else None
        if original is not None:
            menu.addSeparator()
            menu.addMenu(original)
        return menu, commands, original

    def show_context_menu(self, bar, key, watched, position):
        action = self.target_action(bar, watched, position)
        name = self.action_name(bar, action, watched)
        menu, commands, original = self.make_menu(key, name, action)
        old_title = original.title() if original is not None else None
        try:
            if original is not None:
                original.setTitle('原有功能選單')
            selected = menu.exec(position)
        finally:
            if original is not None:
                menu.removeAction(original.menuAction())
                original.setTitle(old_title)
            menu.deleteLater()
        if selected in commands:
            QTimer.singleShot(0, commands[selected])

    def current_layouts(self):
        manager = self.gui.bars_manager
        layouts = {key: tuple(gprefs['action-layout-' + key])
                   for key in ('toolbar', 'toolbar-device', 'toolbar-child', 'searchbar',
                               'menubar', 'menubar-device')}
        layouts['menubar'] = layouts['menubar'] or tuple(manager.menubar_fallback)
        layouts['menubar-device'] = layouts['menubar-device'] or tuple(manager.menubar_device_fallback)
        return layouts

    def edit_layout(self, key, name, operation):
        pref = 'action-layout-' + key
        old = tuple(gprefs[pref])
        new = change_layout(old, name, operation)
        if new == old:
            return
        try:
            if operation == 'remove':
                layouts = self.current_layouts()
                layouts[key] = new
                validate_removal(layouts, key, name, self.gui.iactions.get(name))
            gprefs[pref] = new
            self.gui.bars_manager.init_bars()
            self.gui.bars_manager.update_bars()
        except Exception as err:
            gprefs[pref] = old
            try:
                self.gui.bars_manager.init_bars()
                self.gui.bars_manager.update_bars()
            except Exception:
                pass
            error_dialog(self.gui, '無法變更工具列', str(err), show=True)

    def open_toolbar_settings(self):
        self.gui.iactions['Preferences'].do_config(
            initial_plugin=('Interface', 'Toolbar'), close_after_initial=True)

    def remove_plugin(self, plugin):
        if not getattr(plugin, 'plugin_path', None) or plugin.name in self._removed_plugins:
            return
        if not question_dialog(
                self.gui, '確認移除插件',
                '確定要移除「{}」嗎？<br>移除後需重新啟動 calibre 才會完全生效。'.format(escape(plugin.name)),
                default_yes=False, yes_text='移除插件', no_text='取消', show_copy_button=False):
            return
        try:
            if not uninstall_plugin(plugin):
                raise ValueError('外掛未安裝，或是無法移除的內建外掛。')
        except Exception as err:
            error_dialog(self.gui, '無法移除插件', str(err), show=True)
            return
        self._removed_plugins.add(plugin.name)
        for action in self.gui.iactions.values():
            if getattr(action, 'interface_action_base_plugin', None) is plugin:
                action.qaction.setEnabled(False)
        if plugin is getattr(self, 'interface_action_base_plugin', None):
            self.shutting_down()
        info_dialog(self.gui, '插件已移除', '請重新啟動 calibre，完成移除「{}」。'.format(escape(plugin.name)),
                    show=True, show_copy_button=False)
