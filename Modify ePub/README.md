# Modify ePub

最低 calibre：**3.48.0**；目前外掛版本為 **1.8.11**。

`Modify ePub` 是 calibre 的書庫外掛，讓你可以直接對 EPUB 做清理與小幅修改，而不用先做 ePub->ePub 轉檔。
它適合處理你想保留原始結構、但又需要局部修補內容、資源或中繼資料的情境。

## 目前版本與官方比對

目前版本為 **1.8.11 正體中文整合版**，於 2026-10-23 由本倉庫的 1.8.9 更新。
以 [calibre 官方外掛下載包](https://plugins.calibre-ebook.com/154371.zip) 與 [官方 1.8.11 原始碼](https://github.com/kiwidude68/calibre_plugins/commit/51f4bde27bfb095826bda6e3254ea98e72c4f937) 為比對依據。

| 項目 | 整合結果 |
| --- | --- |
| CSS 邊距解析 | 採用官方 1.8.11 修正，處理 `auto`、`inherit`、負數及不完整的宣告，避免修改 EPUB 時發生例外。 |
| 官方語系 | 整合 1.8.10 的更新，更新簡體中文及法文，新增捷克文、日文、韓文、斯洛伐克文、塞爾維亞文（拉丁字母）及瑞典文。 |
| 本倉庫正體中文 | 保留 `zh_TW`、`zh_Hant`、`zh_Hant_TW` 三個語系檔，確認涵蓋新版全部 127 個介面字串。 |
| 本倉庫其他修改 | 保留中文說明與既有外掛描述。原有邊距處理與官方 1.8.9 相同，可直接套用官方修正。 |
| 其他程式差異 | 同步刪除官方已移除的一行無效註解；共用相容性與圖示檔僅有換行差異，維持原檔。 |

完整更新紀錄見 [CHANGELOG](src/CHANGELOG.md)。

## 功能

- 直接對 EPUB 內容與結構做修改
- 避免轉檔流程帶來的額外重寫與副作用
- 適合做內容清理、格式修補、資源調整
- 內建設定與語系檔，包含正體中文

## 使用方式

1. 在 calibre 書庫中選取要處理的 EPUB。
2. 開啟 `Modify ePub` 外掛。
3. 依照對話框中的選項套用修改。
4. 檢查處理記錄並確認回寫書庫；若設定停用儲存確認，外掛會直接回寫。不需另行轉檔，操作前請先備份。

## 安裝

從 [本倉庫發行頁](https://github.com/SamLaio/calibreMetadatImplode/releases) 下載 `Modify ePub-zh_TW-release.zip`，於 calibre「偏好設定 → 外掛 → 從檔案載入外掛」安裝並重新啟動。

## 原始 GitHub

- [kiwidude68/calibre_plugins](https://github.com/kiwidude68/calibre_plugins/tree/main/modify_epub)

## 結構

- `src/`：解開後的外掛原始碼
- `src/translations/`：語系檔，包含正體中文

## 打包

在倉庫根目錄執行：

```powershell
python build_release.py
```

發布 zip 會輸出到 `dist/Modify ePub-zh_TW-release.zip`。

## 測試

使用 calibre 內附的 Python 執行回歸測試：

```powershell
calibre-debug -e "Modify ePub/tests/test_margins.py"
```

測試涵蓋非數值與負數邊距、一般及不完整的 CSS 宣告、保留較小邊距，以及 CSS／XHTML 改寫後保留其他樣式與內文、重複執行不再修改。
