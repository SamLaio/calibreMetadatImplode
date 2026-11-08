# 本倉庫更新紀錄

## 0.3.1.1 — 2026-11-09

- 採用 calibre 官方外掛索引提供的真正 Hardcover Sync 0.3.1，作者 Juan York，GPL v3；直接加入 175 個訊息目錄項目與三種正體中文語系名稱。
- 維持上游 `hardcover_sync` 名稱空間、API 欄位與設定鍵，與 Goodreads Sync 可同時安裝；本地版號為 0.3.1.1。
- 原本名為 `HardCover Sync.zip` 的檔案其實是 Goodreads Sync 1.16.11。本專案沒有把那包舊 Goodreads 程式當作 Hardcover 發行。
- 驗證獨立載入、中文設定頁、API 金鑰／限流／自動上傳設定儲存，以及與 Goodreads Sync 共存。

- 納入 `build_release.py` 統一打包；隨整合版 v1.3.17 發布。
