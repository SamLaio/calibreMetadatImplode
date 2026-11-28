from qt.core import QToolButton, QPointF, QIcon, QPixmap, QPainter, QPainterPath, QColor, Qt


def cloud_icon():
    pixmap = QPixmap(64, 64)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    path = QPainterPath()
    path.moveTo(17, 49)
    path.cubicTo(1, 49, 1, 27, 16, 26)
    path.cubicTo(17, 6, 43, 5, 48, 25)
    path.cubicTo(65, 23, 68, 49, 49, 49)
    path.closeSubpath()
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor('#56b4e9'))
    painter.drawPath(path)
    painter.end()
    return QIcon(pixmap)


def button_layout(layout, button):
    if layout.indexOf(button) >= 0:
        return layout
    for index in range(layout.count()):
        child = layout.itemAt(index).layout()
        if child is not None:
            found = button_layout(child, button)
            if found is not None:
                return found


class Sidebar:
    """Keep calibre's tree visibility preference separate from the shared pane."""

    def __init__(self, action):
        self.action = action
        self.central = central = action.gui.layout_container
        self.tree = action.tree_pane
        self.bar = action.gui.tb_widget.tb_bar
        self.was_both = False
        self.original_relayout = central.relayout
        central.relayout = self.relayout
        self.original_moves = {}
        for name in ('wide_move_splitter_handle_to', 'narrow_move_splitter_handle_to'):
            original = getattr(central, name)
            self.original_moves[name] = original
            def move(handle, pos, original=original):
                tree = central.is_visible.tag_browser
                if handle is central.left_handle and not tree and action.qaction.isChecked() and action.display_mode() == 'sidebar':
                    # Moving the shared pane must not turn the classification tree on.
                    try:
                        original(handle, QPointF(max(50, pos.x()), pos.y()))
                    finally:
                        central.is_visible.tag_browser = tree
                else:
                    original(handle, pos)
            setattr(central, name, move)
        tree_button = central.tag_browser_button
        layout = button_layout(tree_button.parentWidget().layout(), tree_button)
        if layout is None:
            raise RuntimeError('找不到底部面板切換列。')
        self.button = QToolButton(tree_button.parentWidget())
        self.button.setIcon(cloud_icon())
        self.button.setIconSize(tree_button.iconSize())
        self.button.setToolTip('顯示／隱藏標籤雲')
        self.button.setAccessibleName('標籤雲')
        self.button.setCheckable(True)
        self.button.setChecked(action.qaction.isChecked())
        self.button.toggled.connect(action.qaction.setChecked)
        action.qaction.toggled.connect(self.button.setChecked)
        layout.insertWidget(layout.indexOf(tree_button) + 1, self.button)

    def relayout(self):
        central = self.central
        state = central.is_visible
        tree = state.tag_browser
        cloud = self.action.qaction.isChecked() and self.action.display_mode() == 'sidebar'
        if cloud:
            if central.is_wide:
                central.size_panel_on_initial_show_wide('tag_browser')
            else:
                central.size_panel_on_initial_show_narrow('tag_browser')
        self.tree.setVisible(tree)
        self.bar.setVisible(tree)
        if self.action.display_mode() == 'sidebar':
            self.action.panel.setVisible(cloud)
        # Only geometry uses the combined visibility; saved calibre settings stay intact.
        state.tag_browser = tree or cloud
        try:
            self.original_relayout()
        finally:
            state.tag_browser = tree
        if tree and cloud and not self.was_both:
            from calibre_plugins.tag_cloud.ui import prefs
            self.action.splitter.setSizes(prefs['sizes'])
        self.was_both = tree and cloud
