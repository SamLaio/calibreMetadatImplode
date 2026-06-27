from calibre.customize import InterfaceActionBase


class EmbedMetadataSafePlugin(InterfaceActionBase):
    name = 'Embed Metadata Safe'
    description = (
        'Repair malformed EPUB calibre:user_metadata entries before safely '
        'embedding metadata into selected books.'
    )
    supported_platforms = ['windows', 'osx', 'linux']
    author = 'Codex'
    version = (1, 0, 0)
    minimum_calibre_version = (9, 8, 0)
    actual_plugin = 'calibre_plugins.embed_metadata_safe.ui:EmbedMetadataSafeAction'

    def is_customizable(self):
        return True

    def customization_help(self, gui=False):
        from calibre_plugins.embed_metadata_safe.i18n import build_texts

        return build_texts().settings_help

    def config_widget(self):
        from calibre_plugins.embed_metadata_safe.config import EmbedMetadataSafeConfigWidget

        return EmbedMetadataSafeConfigWidget(self.site_customization)

    def save_settings(self, config_widget):
        self.site_customization = config_widget.get_site_customization()
        actual = getattr(self, 'actual_plugin_', None)
        if actual is not None and hasattr(actual, 'apply_settings'):
            actual.apply_settings()
