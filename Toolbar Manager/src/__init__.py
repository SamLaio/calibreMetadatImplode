from calibre.customize import InterfaceActionBase

__license__ = 'GPL v3'


class ToolbarManager(InterfaceActionBase):
    name = 'Toolbar Manager'
    description = '在工具列右鍵移動或移除按鈕，開啟外掛首頁、選項與工具列設定。'
    author = 'SamLiao & Codex'
    version = (1, 0, 0)
    minimum_calibre_version = (9, 17, 0)
    supported_platforms = ['windows', 'osx', 'linux']
    actual_plugin = 'calibre_plugins.toolbar_manager.ui:ToolbarManagerAction'
    homepage = 'https://github.com/SamLaio/calibreMetadatImplode/tree/main/Toolbar%20Manager'
