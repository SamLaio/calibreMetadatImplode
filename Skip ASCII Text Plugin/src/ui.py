from calibre.gui2.actions import InterfaceAction
from calibre_plugins.skip_ascii_text.config import prefs
from calibre_plugins.skip_ascii_text.main import set_enabled
from calibre_plugins.skip_ascii_text.icons import create_icon


class SkipASCIITextPlugin(InterfaceAction):
    name = 'Skip ASCII Text Plugin'
    action_spec = ('保留原文字元', None, '設定檔名原文字元保留功能', None)

    def genesis(self):
        self.qaction.setIcon(create_icon())
        self.qaction.triggered.connect(self.configure)

    def initialization_complete(self):
        self.apply_settings()

    def configure(self):
        self.interface_action_base_plugin.do_user_config(parent=self.gui)

    def apply_settings(self):
        set_enabled(prefs['SKIP_ASCII_TEXT'])
        state = '已啟用' if prefs['SKIP_ASCII_TEXT'] else '已停用'
        self.qaction.setToolTip('保留原文字元：' + state)
