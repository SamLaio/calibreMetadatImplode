from calibre.customize import EditBookToolPlugin

class TextRegexP0Plugin(EditBookToolPlugin):
    name = 'Enhanced Search and Replace'
    description = '搜尋全書文字類型檔案，提供 Regex 群組預覽、定位及勾選取代'
    supported_platforms = ['windows', 'osx', 'linux']
    author = 'SamLiao & Codex'
    version = (1, 0, 0)
    minimum_calibre_version = (9, 0, 0)
