# 正體中文補強（Traditional Chinese Supplement）

版本：**1.1.2**；作者：**SamLiao & Codex**；授權：GPL v3；最低 calibre：**9.17.0**。
本倉庫自行開發；1.1.2 隨整合版 v1.3.18 發布。

## 用途與支援範圍

在正體中文介面中，自動補齊指定視窗的漏翻標籤、按鈕、群組標題及提示。支援主介面與 Edit Book，不顯示工具列或選單按鈕。

目前對照涵蓋官方「修整書本」、「在網路上分享」及其他官方視窗中混入簡體的指定文字、部分中繼資料編輯視窗，以及 KFX、簡繁轉換、EPUBCheck、XTC、Goodreads、FictionDB、databazeknih、DeACSM、DeDRM、LCPL、Open With、EpubSplit 等外掛的指定顯示文字。不是所有視窗與訊息的完整翻譯。

## 安裝與使用

1. 從 [v1.3.18 發行頁](https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.18) 下載安裝包；自行打包可在根目錄執行 `python -B build_release.py`。
2. 於 calibre「偏好設定 → 外掛 → 從檔案載入外掛」安裝 `Traditional Chinese Supplement-zh_TW-release.zip`。
3. 重啟 calibre 及 Edit Book，介面語言設為正體中文後自動生效，無需手動執行。

支援 `zh_TW`、`zh_Hant`、`zh_Hant_TW`。停用或移除外掛後重新啟動，即恢復原介面。

## 限制

- 精確比對指定來源與已知原文；修正已列入對照的簡體文字，保留其他中文及未知字串。上游修改原文或視窗結構後可能需要更新對照。
- 不改寫書籍、書庫、輸入內容與一般清單／表格／下拉選項值。KFX Input 的通知選項採已測試的專用處理。
- 不包含所有動態訊息、功能選單、轉換記錄、閱讀器，也未提供自訂字典編輯器。
- 補翻發生 Python 例外時，會記錄並略過該元件。

## 來源與測試

來源：[本倉庫](https://github.com/SamLaio/calibreMetadatImplode)。依 calibre 與各外掛原介面的顯示文字建立對照，不打包其程式碼。

Windows、calibre 9.18.0 通過 16 組自動化測試，涵蓋字典、語系、設定值與按鈕訊號保護、例外攔截及無按鈕自動啟用；另有實際外掛面板驗證。未驗收所有版本、平台或外掛完整功能。

```powershell
$env:CALIBRE_CONFIG_DIRECTORY = Join-Path $PWD 'dist/translation-qa/config'
$env:QT_QPA_PLATFORM = 'offscreen'
calibre-debug -e "Traditional Chinese Supplement/tests/test_translation.py"
calibre-debug -e "Traditional Chinese Supplement/tests/test_display.py"
```

1.1.2 掃描本機 9.18.0 的三份官方正體中文目錄，取得 399 筆轉換候選，排除字形歧義後為 310 筆含明確簡體字的文字建立對照，另包含設定標籤冒號形式。僅補強受支援 Qt 元件；動態格式化訊息、國名／語言清單與命令列輸出不保證套用。執行時不依賴文字轉換套件。
