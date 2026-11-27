from calibre.customize import InterfaceActionBase

__license__ = 'GPL v3'


class TagCloud(InterfaceActionBase):
    name = 'Tag Cloud'
    description = '在左側顯示書目詞雲，可勾選來源欄位、點選篩書與自訂配色。'
    author = 'SamLiao & Codex'
    version = (0, 1, 5)
    minimum_calibre_version = (9, 19, 0)
    supported_platforms = ['windows', 'osx', 'linux']
    actual_plugin = 'calibre_plugins.tag_cloud.ui:TagCloudAction'

    def is_customizable(self):
        return True

    def do_user_config(self, parent=None):
        action = getattr(self, 'actual_plugin_', None)
        if action is not None and action.panel is not None:
            action.panel.configure()
        else:
            from calibre.gui2 import info_dialog
            info_dialog(parent, 'Tag Cloud', '請先重新啟動 calibre，再開啟標籤雲設定。', show=True)
