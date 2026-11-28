"""Move the existing cloud between the sidebar and a non-modal window."""
from qt.core import QDialog, QVBoxLayout, QByteArray, Qt
from calibre_plugins.tag_cloud.sidebar import cloud_icon


class FloatingWindow(QDialog):
    def __init__(self, action, preferences):
        super().__init__(action.gui, Qt.WindowType.Window)
        self.action = action
        self.preferences = preferences
        self.closing_app = False
        self.setWindowTitle('浮動標籤雲')
        self.setWindowIcon(cloud_icon())
        self.setModal(False)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.resize(620, 650)
        geometry = preferences['floating_geometry']
        if geometry:
            self.restoreGeometry(QByteArray.fromBase64(geometry.encode('ascii')))

    def save_geometry(self):
        self.preferences['floating_geometry'] = bytes(self.saveGeometry().toBase64()).decode('ascii')

    def hideEvent(self, event):
        self.save_geometry()
        super().hideEvent(event)

    def closeEvent(self, event):
        self.save_geometry()
        if self.closing_app:
            event.accept()
        else:
            event.ignore()
            self.action.qaction.setChecked(False)

    def reject(self):
        self.save_geometry()
        self.action.qaction.setChecked(False)


class Presentation:
    def __init__(self, action, preferences):
        self.action = action
        self.preferences = preferences
        self.window = FloatingWindow(action, preferences)
        self.set_mode(preferences['display_mode'])

    def set_mode(self, mode):
        if mode not in ('sidebar', 'floating'):
            mode = 'sidebar'
        action = self.action
        panel = action.panel
        if mode == 'floating' and panel.parentWidget() is not self.window:
            action.save_sizes()
            self.window.layout().addWidget(panel)
        elif mode == 'sidebar' and panel.parentWidget() is not action.splitter:
            self.window.save_geometry()
            self.window.hide()
            action.splitter.addWidget(panel)
            action.splitter.setCollapsible(1, False)
            action.splitter.setSizes(self.preferences['sizes'])
        self.preferences['display_mode'] = mode
        self.update_visibility()
        if hasattr(action, 'sidebar'):
            action.sidebar.relayout()

    def update_visibility(self):
        visible = self.action.qaction.isChecked()
        self.action.panel.setVisible(visible)
        self.window.setVisible(visible and self.action.display_mode() == 'floating')

    def toggle_cloud(self):
        self.action.qaction.setChecked(not self.action.qaction.isChecked())
        if self.action.qaction.isChecked() and self.action.display_mode() == 'floating':
            self.window.showNormal()
            self.window.raise_()
            self.window.activateWindow()

    def shutdown(self):
        self.window.closing_app = True
        self.window.save_geometry()
        self.window.hide()
