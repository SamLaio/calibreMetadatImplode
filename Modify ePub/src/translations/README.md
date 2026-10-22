# Translations

If you're interested in helping provide translations for this project,
please use the
[Transifex](https://www.transifex.com/projects/p/calibre-plugins/resources/)
website to add translations to this, or other calibre plugins that support it.

## 本倉庫正體中文

1.8.11 的正體中文涵蓋 127 個介面字串，包含內容相同的 `zh_TW.mo`、`zh_Hant.mo` 與 `zh_Hant_TW.mo`。本倉庫目前僅收錄這三個正體中文編譯檔，未附正體中文 `.po` 來源。

官方語系 `.mo` 取自 1.8.11 發行包。`build_release.py` 只負責封裝，不會編譯翻譯；安裝包包含 `.mo`，排除 `.po`。更新正體中文編譯檔時須同步三個語系別名。
