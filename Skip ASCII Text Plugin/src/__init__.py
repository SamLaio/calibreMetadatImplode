from calibre.customize import InterfaceActionBase

__license__ = 'GPL v3'


class SkipASCIIText(InterfaceActionBase):
    name = 'Skip ASCII Text Plugin'
    description = '保留檔名中的中文等原文字元，可隨時切換與還原。'
    author = 'SamLiao & Codex'
    version = (1, 0, 1)
    minimum_calibre_version = (5, 0, 0)
    supported_platforms = ['windows', 'osx', 'linux']
    actual_plugin = 'calibre_plugins.skip_ascii_text.ui:SkipASCIITextPlugin'

    def is_customizable(self):
        return True

    def config_widget(self):
        from calibre_plugins.skip_ascii_text.config import ConfigWidget
        return ConfigWidget()

    def save_settings(self, widget):
        widget.save_settings()
        action = getattr(self, 'actual_plugin_', None)
        if action is not None:
            action.apply_settings()

    def do_user_config(self, parent=None):
        from calibre_plugins.skip_ascii_text.config import SettingsDialog
        dialog = SettingsDialog(parent)
        if dialog.exec_():
            self.save_settings(dialog.settings)
            return True
        return False
