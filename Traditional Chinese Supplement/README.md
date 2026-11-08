# 正體中文補強（Traditional Chinese Supplement）

版本：**1.1.1**；作者：**SamLiao & Codex**；授權：GPL v3；最低 calibre：**9.17.0**。
本倉庫自行開發，不是 calibre 或各第三方外掛的官方翻譯版本。本版隨整合版 v1.3.17 發布。

## 用途與範圍

在主介面與 Edit Book 載入後補翻指定視窗，不需調整外掛順序。開啟新視窗時也會套用。

- 官方「修整書本」八個漏翻選項、相關說明；單本／批次中繼資料視窗的部分漏翻標籤。
- KFX Input 設定與轉換選項、KFX Output、Chinese Text Conversion、EPUBCheck、XTC Output。
- Goodreads、FictionDB、databazeknih.cz、DeACSM、DeDRM、LCPL Input、Open With、EpubSplit 的已知標籤、按鈕與提示。
- Goodreads Sync／原誤標的 HardCover 包與 Markdown Output 已加入部分對照；其後另將三個正確來源的外掛直接中文化，見各外掛 README。

本版新增 317 條指定範圍對照及 12 條共用對照，保留 1.0.0 的修整書本與 KFX Input 專用處理。
僅在正體中文介面（`zh_TW`、`zh_Hant`、`zh_Hant_TW`）生效；依視窗來源及原文精確比對，已有中文與未知字串會保留。

工具列與 Edit Book 均不顯示入口按鈕；若舊版按鈕已放入工具列，更新後重新啟動即會隱藏。

安裝包見 [v1.3.17 發行頁](https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.17)。

## 安裝與使用

1. 在倉庫根目錄執行 `python -B build_release.py`，取得 `dist/Traditional Chinese Supplement-zh_TW-release.zip`。
2. 在 calibre「偏好設定 → 外掛 → 從檔案載入外掛」安裝，重啟 calibre 及已開啟的 Edit Book。
3. 確認介面語言為正體中文；開啟支援的視窗即自動生效，不提供工具列或選單按鈕，也不需要手動執行。

停用或移除後重新啟動即可恢復原介面；不修改原外掛安裝包、calibre 安裝檔、書籍及書庫。

## 安全邊界與限制

- 一般下拉選項、表格／清單資料、文字輸入欄與書籍內文不改寫。有些外掛會用英文選項文字判斷功能，保留這些文字可避免設定失效。KFX Input 的三個通知選項已另測索引及儲存結果，沿用專用處理。
- 只補已知標籤、按鈕、群組標題與提示；不是所有外掛的全面翻譯，也不包含所有動態訊息、功能選單、轉換記錄或閱讀器。
- 每次補翻若發生 Python 例外，會記錄並略過該元件，不讓例外逸出 Qt 事件過濾器。
- 實際外掛驗收以本機安裝版本為準；上游改動原文、結構或設定方式後需要重新核對。未加入自訂字典編輯器。

## 測試結果與已知問題

Windows、calibre **9.18.0**：15 組自動化測試通過，包含全部字典條目、正體中文／其他語系、既有中文保留、輸入／模型／按鈕訊號、重複套用、故障注入、主介面與 Edit Book 入口，以及實際官方對話框與測試書庫不變。

另從原安裝 ZIP 載入外掛，完成 **13 個實際外掛面板**測試：KFX Input，以及 Goodreads、FictionDB、databazeknih.cz、KFX Output、LCPL Input、EPUBCheck、EpubSplit、Open With、DeACSM、DeDRM、Chinese Text Conversion、XTC Output。測試保留欄位、下拉索引、內部資料、勾選狀態；其中後十二個面板均比較翻譯前後的設定儲存結果，KFX Input 另驗證三種索引儲存。

2026-11-09 更正與後續處理：

- Goodreads Sync 1.17.6 的屬性錯誤來自不完整的測試主視窗，不是原外掛缺少該屬性。補齊測試替身後原版可正常開啟、儲存；專案另提供直接中文化的 1.17.6.1。
- 原 `HardCover Sync.zip` 其實是舊版 Goodreads Sync 1.16.11；其 `RECOVER_PARSER` 錯誤不屬於真正的 Hardcover。專案已另匯入真正的 Hardcover Sync 0.3.1，提供直接中文化的 0.3.1.1。
- Markdown Output 1.0.3 的 `gridLayout` 相容性錯誤已在獨立的 1.0.3.1 修正。

未在使用者書庫回寫，也未對全部外掛執行聯網、帳號授權、DRM 處理或完整書檔轉換；因此不能視為這些外掛全部功能均已驗收。

```powershell
$env:CALIBRE_CONFIG_DIRECTORY = Join-Path $PWD 'dist/translation-qa/config'
$env:QT_QPA_PLATFORM = 'offscreen'
calibre-debug -e "Traditional Chinese Supplement/tests/test_translation.py"
calibre-debug -e "Traditional Chinese Supplement/tests/test_display.py"
```

實際面板測試工具為 `tests/check_installed_plugin.py`，需使用本機原安裝 ZIP，並將 `CALIBRE_CONFIG_DIRECTORY` 設在本專案 `dist/` 下；它會在獨立設定與測試書庫比較翻譯前後儲存結果。測試畫面及報告輸出於 `dist/`，不會上傳帳號資料。

## 來源

- [本倉庫](https://github.com/SamLaio/calibreMetadatImplode)，作者 SamLiao & Codex。
- [calibre 官方 Polish 視窗](https://github.com/kovidgoyal/calibre/blob/v9.18.0/src/calibre/gui2/actions/polish.py)與 [Edit Book 外掛介面](https://github.com/kovidgoyal/calibre/blob/v9.18.0/src/calibre/gui2/tweak_book/plugin.py)。
- 翻譯原文以 2026-11-08 本機已安裝外掛核對；KFX Input 2.34.2 原作者 John Howell（jhowell）。未將第三方外掛程式碼打包。
