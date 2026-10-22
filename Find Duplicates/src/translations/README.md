# Translations

If you're interested in helping provide translations for this project,
please use the
[Transifex](https://www.transifex.com/projects/p/calibre-plugins/resources/)
website to add translations to this, or other calibre plugins that support it.

## 本倉庫正體中文

1.10.11 的正體中文涵蓋 179 個介面字串。保留 `zh_TW.po` 翻譯來源，並以相同內容提供 `zh_TW.mo`、`zh_Hant.mo` 與 `zh_Hant_TW.mo`，支援不同語系代碼。

官方語系 `.mo` 取自 1.10.11 發行包。`build_release.py` 只負責封裝，不會編譯翻譯；安裝包包含 `.mo`，排除 `.po`。調整正體中文後須重新編譯並同步三個 `.mo`。
