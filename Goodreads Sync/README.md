# Goodreads Sync

版本：**1.17.6.1**；原作者：**Grant Drake**。基於上游 **1.17.6**，本倉庫負責正體中文與下列修訂；隨整合版 v1.3.17 發布。

## 用途

在 calibre 與 Goodreads 之間同步書架、標籤、評分、書評與閱讀進度。

安裝包見 [v1.3.17 發行頁](https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.17)。

## 安裝與使用

1. 在根目錄執行 `python -B build_release.py`，取得 `dist/Goodreads Sync-zh_TW-release.zip`。
2. 在 calibre「偏好設定 → 外掛 → 從檔案載入外掛」安裝並重新啟動。
3. 在「偏好設定 → 外掛」自訂此外掛；依需要從「工具列與選單」加入按鈕，再設定帳號、欄位與同步方向。

此外掛直接提供中文，不依賴「正體中文補強」外掛。

## 本倉庫修改

- 以本機原版 1.17.6 匯入，保留原作者、GPL v3 宣告、內部設定鍵與同步流程。
- 直接加入 315 個訊息目錄項目，含正體中文與 `zh_Hant`、`zh_Hant_TW` 別名；ISBN、品牌與快捷鍵等識別文字保留。
- 自訂欄位 helper 在原程式已存在。先前測試報出的屬性錯誤，是測試主視窗缺少 `must_restart_before_config` 等屬性；補齊測試環境後原版即可正常設定，未以不必要的核心改寫掩蓋問題。
- 驗證中文設定頁、使用者資料與設定儲存、欄位 helper，以及 ADD／REMOVE 內部選項值。

## 來源

[原始專案／討論串](https://github.com/kiwidude68/calibre_plugins/tree/main/goodreads_sync)。匯入日期：2026-11-09。

本機原安裝包 SHA-256：`ba868d409f40f5682999c384d5ba70e05c32b82f084ff9615ae02a74176d2129`。

## 測試與限制

Windows、calibre 9.18.0 已通過設定頁、版本與相關功能測試；翻譯目錄另核對格式佔位符及三種語系別名。

同步會變更書庫或遠端資料，請先備份並核對方向。測試使用獨立設定與測試書庫、封鎖網路，未以真實帳號驗收完整遠端同步。

```powershell
$env:CALIBRE_CONFIG_DIRECTORY = Join-Path $PWD 'dist/standalone-qa/config'
$env:QT_QPA_PLATFORM = 'offscreen'
calibre-debug -e "Goodreads Sync/tests/test_goodreads_sync.py"
python -B "Goodreads Sync/tests/test_catalog.py"
```
