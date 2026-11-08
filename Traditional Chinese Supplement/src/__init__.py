from calibre.customize import EditBookToolPlugin, InterfaceActionBase

__license__ = 'GPL v3'


class TraditionalChineseSupplement(InterfaceActionBase, EditBookToolPlugin):
    name = 'Traditional Chinese Supplement'
    description = '補齊指定 calibre 與第三方外掛視窗的正體中文顯示文字。'
    author = 'SamLiao & Codex'
    version = (1, 1, 2)
    minimum_calibre_version = (9, 17, 0)
    supported_platforms = ['windows', 'osx', 'linux']
    actual_plugin = 'calibre_plugins.traditional_chinese_supplement.ui:TranslationAction'
    homepage = 'https://github.com/SamLaio/calibreMetadatImplode/tree/main/Traditional%20Chinese%20Supplement'
