from calibre.customize import InterfaceActionBase

__license__ = 'GPL v3'


class VirtualLibraryBuilder(InterfaceActionBase):
    name = 'Virtual Library Builder'
    description = '建立及修改 calibre 原生虛擬書庫。'
    author = 'SamLiao & Codex'
    version = (0, 1, 11)
    minimum_calibre_version = (9, 19, 0)
    supported_platforms = ['windows', 'osx', 'linux']
    actual_plugin = 'calibre_plugins.virtual_library_builder.ui:BuilderAction'
