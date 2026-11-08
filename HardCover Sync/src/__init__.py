from calibre.customize import InterfaceActionBase

from ._version import __version_tuple__


class HardcoverSyncPlugin(InterfaceActionBase):
    name = "Hardcover Sync"
    description = (
        "雙向同步 calibre 與 Hardcover 的清單、評分、書評、閱讀狀態、筆記、引文及標籤，並擷取書籍 ISBN"
    )
    supported_platforms = ["windows", "osx", "linux"]
    author = "Juan York"
    version = __version_tuple__
    minimum_calibre_version = (7, 7, 0)

    actual_plugin = "calibre_plugins.hardcover_sync.ui:HardcoverSyncAction"

    def is_customizable(self):
        return True

    def config_widget(self):
        from calibre_plugins.hardcover_sync.config_widget import ConfigWidget

        return ConfigWidget()

    def save_settings(self, config_widget):
        config_widget.save_settings()
