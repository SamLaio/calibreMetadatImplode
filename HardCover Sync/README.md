# Hardcover Sync

版本：**0.3.1.1**；原作者：**Juan York**。基於上游 **0.3.1**，本倉庫負責正體中文與下列修訂；隨整合版 v1.3.17 發布。

## 用途

與 Hardcover 同步清單、評分、書評、閱讀狀態、筆記與引文，並可從書籍內文擷取 ISBN。

安裝包見 [v1.3.17 發行頁](https://github.com/SamLaio/calibreMetadatImplode/releases/tag/v1.3.17)。

## 安裝與使用

1. 在根目錄執行 `python -B build_release.py`，取得 `dist/Hardcover Sync-zh_TW-release.zip`。
2. 在 calibre「偏好設定 → 外掛 → 從檔案載入外掛」安裝並重新啟動。
3. 在「偏好設定 → 外掛」自訂此外掛；依需要從「工具列與選單」加入按鈕，再設定帳號、欄位與同步方向。

若目前有兩個 Goodreads Sync，請先核對版本：移除原本誤標為 HardCover 的 **Goodreads Sync 1.16.11**，保留正常的 Goodreads Sync，再安裝真正的 Hardcover Sync。勿將兩個服務的帳號或 API 金鑰混用；本次沒有更動您日常 calibre 的外掛或設定。

此外掛直接提供中文，不依賴「正體中文補強」外掛。

## 本倉庫修改

- 採用 calibre 官方外掛索引提供的真正 Hardcover Sync 0.3.1，作者 Juan York，GPL v3；直接加入 175 個訊息目錄項目與三種正體中文語系名稱。
- 維持上游 `hardcover_sync` 名稱空間、API 欄位與設定鍵，與 Goodreads Sync 可同時安裝；本地版號為 0.3.1.1。
- 原本名為 `HardCover Sync.zip` 的檔案其實是 Goodreads Sync 1.16.11。本專案沒有把那包舊 Goodreads 程式當作 Hardcover 發行。
- 驗證獨立載入、中文設定頁、API 金鑰／限流／自動上傳設定儲存，以及與 Goodreads Sync 共存。

## 來源

[原始專案／討論串](https://github.com/jojuyo/calibre-hardcover-sync-plugin)。匯入日期：2026-11-09。

官方安裝包：[373995.zip](https://plugins.calibre-ebook.com/373995.zip)，SHA-256：`a9198fa0f04d5bd8de2b83a80eb9bf60d9fc33757938417db390768a7af36c2b`。

## 測試與限制

Windows、calibre 9.18.0 已通過設定頁、版本與相關功能測試；翻譯目錄另核對格式佔位符及三種語系別名。

同步會變更書庫或遠端資料，請先備份並核對方向。測試使用獨立設定與測試書庫、封鎖網路，未以真實帳號驗收完整遠端同步。

```powershell
$env:CALIBRE_CONFIG_DIRECTORY = Join-Path $PWD 'dist/standalone-qa/config'
$env:QT_QPA_PLATFORM = 'offscreen'
calibre-debug -e "HardCover Sync/tests/test_hardcover_sync.py"
python -B "HardCover Sync/tests/test_catalog.py"
```

Windows 注意：若 `HardCover Sync` 與 `Hardcover Sync` 兩筆紀錄指向同一檔案，不要直接刪除其中一個安裝包。先關閉 calibre 並備份設定，再清除舊大小寫名稱的重複登記，保留新版 ZIP 與帳號資料。
