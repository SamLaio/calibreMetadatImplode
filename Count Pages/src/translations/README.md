# 翻譯

如果你想協助這個專案翻譯，
請使用 [Transifex](https://www.transifex.com/projects/p/calibre-plugins/resources/)
網站，為這個專案或其他支援的 calibre 外掛新增翻譯。

## 本倉庫正體中文

1.15.3 的正體中文涵蓋 119 個介面字串，翻譯來源為 `zh_TW.po`，編譯結果需同步至 `zh_TW.mo`、`zh_Hant.mo` 與 `zh_Hant_TW.mo`。

`build_release.py` 只負責封裝，不會編譯翻譯；安裝包包含 `.mo`，排除 `.po`。調整翻譯後請重新編譯並執行 `Count Pages/tests/test_update.py` 的覆蓋率測試。
