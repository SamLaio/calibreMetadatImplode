# Translations

If you're interested in helping provide translations for this project,
please use the
[Transifex](https://www.transifex.com/projects/p/calibre-plugins/resources/)
website to add translations to this, or other calibre plugins that support it.

## 本倉庫正體中文

本倉庫 3.12.0 修訂版保留 `zh_TW.po`，並提供內容相同的 `zh_TW.mo`、`zh_Hant.mo` 與 `zh_Hant_TW.mo`。

`build_release.py` 只負責封裝，不會編譯翻譯；安裝包包含現有 `.mo`，排除 `.po`。其他上游語系目前保留為 `.po` 來源，尚未附對應 `.mo`；調整或啟用這些翻譯時須先編譯。
